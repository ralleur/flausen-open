// SPDX-License-Identifier: MIT
// Explicitly loaded test plugin; never installed or loaded by the normal wrapper.
#include <QApplication>
#include <QAction>
#include <QDialog>
#include <QDir>
#include <QFile>
#include <QGenericPlugin>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QKeyEvent>
#include <QTimer>
#include <QWidget>
#include <QTabBar>
#include <QGraphicsView>
#include <QGraphicsScene>
#include <QEventLoop>
#include <KXmlGuiWindow>
#include <KActionCollection>
#include <KIconLoader>
#include <KIconTheme>
#include <QToolButton>
#include <QPlainTextEdit>

class PreviewProbe : public QGenericPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QGenericPluginFactoryInterface_iid FILE "live_preview_probe.json")
public:
    QObject *create(const QString &key,const QString &) override {
        const auto output=qEnvironmentVariable("RALLEUR_PREVIEW_PROBE_DIR");
        if (key!="ralleurpreviewprobe" || output.isEmpty()) return nullptr;
        auto lifetime=new QObject;
        QTimer::singleShot(2500,lifetime,[output] {
            QJsonObject report;
            QWidget *window=nullptr,*view=nullptr;
            for(auto w:QApplication::topLevelWidgets()) if(w->inherits("DolphinMainWindow")) window=w;
            if(window) for(auto w:window->findChildren<QWidget *>()) if(w->inherits("DolphinView") && w->isVisible()) {view=w;break;}
            auto send=[](QWidget *target,int key,bool repeat=false) {
                QKeyEvent override(QEvent::ShortcutOverride,key,Qt::NoModifier);
                QApplication::sendEvent(target,&override);
                QKeyEvent press(QEvent::KeyPress,key,Qt::NoModifier,QString(),repeat);
                QApplication::sendEvent(target,&press);
                QKeyEvent release(QEvent::KeyRelease,key,Qt::NoModifier);
                QApplication::sendEvent(target,&release);
            };
            auto visibleDialog=[window]() -> QDialog * {
                if(window) for(auto d:window->findChildren<QDialog *>("ralleurQuickPreviewDialog")) if(d->isVisible()) return d;
                return nullptr;
            };
            report["viewFound"]=view!=nullptr;
            if(view) {
                QEventLoop ready;QTimer::singleShot(100,&ready,&QEventLoop::quit);ready.exec();
                report["selectAllInvoked"]=QMetaObject::invokeMethod(view,"selectAll",Qt::DirectConnection);
                report["flushSlot"]=view->metaObject()->indexOfSlot("emitSelectionChangedSignal()");
                window->grab().save(output+"/before.png");
                view->setFocus();
                send(view,Qt::Key_Space);
                auto dialog=visibleDialog();
                report["opened"]=dialog!=nullptr;
                if(dialog) {
                    report["imageShown"]=dialog->findChild<QWidget *>("ralleurImagePreview")!=nullptr;
                    dialog->grab().save(output+"/preview.png");
                    if(qEnvironmentVariableIsSet("RALLEUR_SELECTION_PROBE")) {
                        const auto geometry=dialog->geometry();
                        window->activateWindow();
                        QWidget *fileContainer=nullptr;
                        for(auto child:view->findChildren<QWidget *>()) if(child->inherits("KItemListContainer")) fileContainer=child;
                        if(fileContainer) {
                            fileContainer->setFocus();
                            QEventLoop focus;QTimer::singleShot(100,&focus,&QEventLoop::quit);focus.exec();
                            send(fileContainer,Qt::Key_End);
                            QEventLoop selection;QTimer::singleShot(600,&selection,&QEventLoop::quit);selection.exec();
                        }
                        auto text=dialog->findChild<QPlainTextEdit *>("ralleurTextPreview");
                        report["selectionFollowed"]=text && text->toPlainText().contains("dynamic selection probe");
                        report["samePreviewWindow"]=visibleDialog()==dialog && dialog->geometry()==geometry;
                        report["selectionTitle"]=dialog->windowTitle();
                        report["selectionFocus"]=qApp->focusWidget()?qApp->focusWidget()->metaObject()->className():"none";
                        dialog->grab().save(output+"/selection-text.png");
                    }
                    send(dialog,Qt::Key_Space,true);
                    report["repeatKeptOpen"]=dialog->isVisible();
                    send(dialog,Qt::Key_Space);
                    report["secondSpaceClosed"]=!dialog->isVisible();
                    send(view,Qt::Key_Space);
                    dialog=visibleDialog();
                    report["reopened"]=dialog!=nullptr;
                    if(dialog) {send(dialog,Qt::Key_Escape);report["escapeClosed"]=!dialog->isVisible();}
                }
                if(auto native=qobject_cast<KXmlGuiWindow *>(window)) {
                    if(auto action=native->actionCollection()->action("toggle_selection_mode")) {
                        report["selectionModeOff"]=!action->isChecked();
                        report["spaceRemovedFromSelectionMode"]=!action->shortcuts().contains(QKeySequence(Qt::Key_Space));
                    }
                }
            }
            if(window && qEnvironmentVariableIsSet("RALLEUR_THEME_PROBE")) {
                auto loader=KIconLoader::global();
                report["iconTheme"]=loader->theme()?loader->theme()->name():QString();
                report["followsColors"]=loader->theme() && loader->theme()->followsColorScheme();
                const auto original=qApp->palette();
                bool themePassed=true;
                int number=0;
                for(const auto &background:{QColor("#1d2022"),QColor("#193047"),QColor("#faf7f2")}) {
                    const bool dark=background.lightness()<128;
                    auto theme=original;
                    theme.setColor(QPalette::Window,background);
                    theme.setColor(QPalette::Base,dark?background.darker(120):QColor("#fffdfa"));
                    theme.setColor(QPalette::WindowText,dark?QColor("#f2f3f4"):QColor("#18212a"));
                    theme.setColor(QPalette::Text,theme.color(QPalette::WindowText));
                    theme.setColor(QPalette::Button,background);
                    theme.setColor(QPalette::ButtonText,theme.color(QPalette::WindowText));
                    theme.setColor(QPalette::Highlight,dark?QColor("#de8276"):QColor("#345b9e"));
                    theme.setColor(QPalette::AlternateBase,dark?background.lighter(115):QColor("#eeeae4"));
                    qApp->setPalette(theme);
                    QEventLoop settle;QTimer::singleShot(100,&settle,&QEventLoop::quit);settle.exec();
                    for(auto widget:window->findChildren<QWidget *>()) {
                        if(widget->inherits("KUrlNavigator") || qobject_cast<QTabBar *>(widget)) {
                            themePassed &= widget->palette().color(QPalette::Window)==background;
                            themePassed &= widget->palette().color(QPalette::WindowText)==theme.color(QPalette::WindowText);
                        }
                        if(widget->inherits("DolphinView")) {
                            auto base=theme.color(QPalette::Base);
                            if(base.lightness()<100) base=QColor(base.red()+10,base.green()+10,base.blue()+10);
                            themePassed &= widget->palette().color(QPalette::Base)==base;
                            for(auto graphics:widget->findChildren<QGraphicsView *>()) if(graphics->scene()) {
                                themePassed &= graphics->scene()->palette().color(QPalette::Text)==theme.color(QPalette::Text);
                                themePassed &= graphics->scene()->palette().color(QPalette::Highlight)==theme.color(QPalette::Highlight);
                            }
                        }
                    }
                    window->grab().save(output+QStringLiteral("/theme-%1.png").arg(++number));
                    if(!dark) {
                        QJsonArray labels;
                        for(auto widget:window->findChildren<QWidget *>()) if(widget->isVisible() && widget->inherits("QLabel")) {
                            labels.append(QJsonObject{{"class",widget->metaObject()->className()},{"name",widget->objectName()},
                                {"text",widget->property("text").toString().left(90)},
                                {"textColor",widget->palette().color(widget->foregroundRole()).name()},
                                {"style",widget->styleSheet()}});
                        }
                        report["lightLabels"]=labels;
                        if(auto close=window->findChild<QToolButton *>("ralleurClose")) {
                            const auto image=close->icon().pixmap(16,16).toImage();
                            report["closeIconName"]=close->icon().name();
                            int red=0,green=0,blue=0,count=0;
                            for(int y=0;y<image.height();++y) for(int x=0;x<image.width();++x) {
                                const auto pixel=image.pixelColor(x,y);
                                if(pixel.alpha()>180) {red+=pixel.red();green+=pixel.green();blue+=pixel.blue();++count;}
                            }
                            report["closeIconColor"]=count?QColor(red/count,green/count,blue/count).name():QStringLiteral("empty");
                        }
                    }
                }
                qApp->setPalette(original);
                report["liveThemeChanges"]=themePassed;
            }
            bool passed=true;
            for(const auto &name:{"viewFound","opened","imageShown","repeatKeptOpen","secondSpaceClosed","reopened","escapeClosed","selectionModeOff","spaceRemovedFromSelectionMode"}) passed &= report.value(name).toBool();
            if(qEnvironmentVariableIsSet("RALLEUR_THEME_PROBE")) passed &= report.value("liveThemeChanges").toBool();
            if(qEnvironmentVariableIsSet("RALLEUR_SELECTION_PROBE")) passed &= report.value("selectionFollowed").toBool() && report.value("samePreviewWindow").toBool();
            report["passed"]=passed;
            QFile file(output+"/result.json");if(file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(report).toJson());
            if(window) QMetaObject::invokeMethod(window,"quit",Qt::QueuedConnection);
        });
        return lifetime;
    }
};
#include "live_preview_probe.moc"
