#include <KLocalizedString>
// SPDX-License-Identifier: GPL-3.0-only
#include "kcmhost.h"
#include <KQuickConfigModule>
#include <KQuickConfigModuleLoader>
#include <KPluginMetaData>
#include <QQmlEngine>
#include <QQuickWindow>
#include <QLibraryInfo>
#include <QDir>
#include <QRegularExpression>
#include <QEvent>
#include <QTimer>
#include <QCloseEvent>

static KPluginMetaData metadata(const QString &id) {
    if(!QRegularExpression(QStringLiteral("^kcm_[a-zA-Z0-9_-]+$")).match(id).hasMatch()) return {};
    for(const auto &dir: {QStringLiteral("plasma/kcms/systemsettings"),QStringLiteral("plasma/kcms")}) {
        auto md=KPluginMetaData::findPluginById(dir,id);
        if(md.isValid())return md;
    }
    return {};
}
bool WindowCloseGuard::eventFilter(QObject *object,QEvent *event){
    if(event->type()==QEvent::Close && m_dirty->load()){
        static_cast<QCloseEvent*>(event)->ignore();emit blocked();return true;
    }
    return QObject::eventFilter(object,event);
}
KcmHost::KcmHost(QQuickItem *parent):QQuickItem(parent) {
    connect(this,&KcmHost::changed,this,[this]{m_dirty->store(needsSave());});
    connect(this,&QQuickItem::windowChanged,this,[this](QQuickWindow *win){
        if(m_guard)m_guard->deleteLater();
        m_window=win;
        if(!win)return;
        auto *guard=new WindowCloseGuard(m_dirty);m_guard=guard;
        guard->moveToThread(win->thread());
        connect(guard,&WindowCloseGuard::blocked,this,&KcmHost::closeBlocked,Qt::QueuedConnection);
        QMetaObject::invokeMethod(win,[guard,win]{guard->setParent(win);win->installEventFilter(guard);},Qt::QueuedConnection);
    });
}
KcmHost::~KcmHost(){m_dirty->store(false);if(m_guard)m_guard->deleteLater();clear();}
void KcmHost::componentComplete(){QQuickItem::componentComplete();m_complete=true;load();}
void KcmHost::setModuleId(const QString &id){if(m_id==id)return;m_id=id;emit moduleIdChanged();if(m_complete)load();}
bool KcmHost::ready()const{return m_module && !m_pages.isEmpty();}
bool KcmHost::needsSave()const{return m_module && m_module->needsSave();}
bool KcmHost::canDefault()const{return m_module && (m_module->buttons() & KAbstractConfigModule::Default);}
int KcmHost::depth()const{return m_pages.size();}
QQuickItem *KcmHost::page()const{return m_pages.isEmpty()?nullptr:m_pages.value(qBound(0,m_module ? m_module->currentIndex() : 0,int(m_pages.size()-1))).data();}
void KcmHost::clear(){
    for(auto item:m_pages)if(item)item->setParentItem(nullptr);
    m_pages.clear();
    delete m_module.data();m_module=nullptr;
}
void KcmHost::load(){
    clear();m_error.clear();emit changed();
    if(m_id.isEmpty())return;
    auto md=metadata(m_id);
    if(!md.isValid()){m_error=i18nd("flausen", "This settings module is not installed: %1").arg(m_id);emit changed();return;}
    auto *engine=qmlEngine(this);
    auto result=KQuickConfigModuleLoader::loadModule(md,this,{},std::shared_ptr<QQmlEngine>(engine,[](QQmlEngine*){}));
    if(!result){m_error=result.errorString;emit changed();return;}
    m_module=result.plugin;
    auto *module=m_module.data();
    connect(module,&KQuickConfigModule::needsSaveChanged,this,&KcmHost::changed);
    connect(module,&KQuickConfigModule::buttonsChanged,this,&KcmHost::changed);
    connect(module,&KQuickConfigModule::currentIndexChanged,this,[this]{layout();emit changed();});
    connect(module,&KQuickConfigModule::pagePushed,this,[this](QQuickItem *item){attach(item);});
    connect(module,&KQuickConfigModule::pageRemoved,this,[this]{
        if(m_pages.size()>1)m_pages.removeLast();layout();emit changed();
    });
    auto install=[this]{
        if(!m_module)return;
        auto *ui=m_module->mainUi();
        if(!ui){m_error=m_module->errorString();emit changed();return;}
        if(!m_pages.contains(ui)){ui->setParentItem(this);m_pages.prepend(ui);layout();m_module->load();emit changed();}
    };
    connect(module,&KQuickConfigModule::mainUiReady,this,install);
    install();
}
void KcmHost::attach(QQuickItem *item){if(!item || m_pages.contains(item))return;item->setParentItem(this);m_pages.append(item);layout();emit changed();}
void KcmHost::layout(){for(auto item:m_pages)if(item){item->setVisible(item==page());item->setPosition({0,0});item->setSize(size());}}
void KcmHost::geometryChange(const QRectF &n,const QRectF &o){QQuickItem::geometryChange(n,o);layout();}
void KcmHost::save(){if(m_module){m_module->save();emit changed();}}
void KcmHost::reset(){if(m_module){m_module->load();emit changed();}}
void KcmHost::defaults(){if(m_module){m_module->defaults();emit changed();}}
void KcmHost::back(){if(m_module && m_pages.size()>1)m_module->pop();}
QStringList KcmHost::availableModules()const{
    QStringList ids;
    for(auto dir:{QStringLiteral("plasma/kcms/systemsettings"),QStringLiteral("plasma/kcms")})
        for(const auto &md:KPluginMetaData::findPlugins(dir))ids<<md.pluginId();
    ids.removeDuplicates();ids.sort();return ids;
}

QVariantList KcmHost::catalogue()const{
    QVariantList entries;QStringList seen;
    for(auto dir:{QStringLiteral("plasma/kcms/systemsettings"),QStringLiteral("plasma/kcms")})
        for(const auto &md:KPluginMetaData::findPlugins(dir)){
            if(seen.contains(md.pluginId()))continue;
            seen<<md.pluginId();
            entries<<QVariantMap{{"id",md.pluginId()},{"name",md.name()},{"description",md.description()},{"icon",md.iconName()}};
        }
    std::sort(entries.begin(),entries.end(),[](const QVariant &a,const QVariant &b){return QString::localeAwareCompare(a.toMap().value("name").toString(),b.toMap().value("name").toString())<0;});
    return entries;
}
