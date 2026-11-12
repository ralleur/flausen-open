// SPDX-License-Identifier: GPL-3.0-only
#pragma once
#include <QQuickItem>
#include <QPointer>
#include <qqmlintegration.h>
#include <memory>
#include <atomic>
class KQuickConfigModule;
class WindowCloseGuard:public QObject {
    Q_OBJECT
public:
    explicit WindowCloseGuard(std::shared_ptr<std::atomic_bool> dirty):m_dirty(std::move(dirty)){}
signals:
    void blocked();
protected:
    bool eventFilter(QObject *object,QEvent *event) override;
private:
    std::shared_ptr<std::atomic_bool> m_dirty;
};
class KcmHost : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString moduleId READ moduleId WRITE setModuleId NOTIFY moduleIdChanged)
    Q_PROPERTY(QString error READ error NOTIFY changed)
    Q_PROPERTY(bool ready READ ready NOTIFY changed)
    Q_PROPERTY(bool needsSave READ needsSave NOTIFY changed)
    Q_PROPERTY(bool canDefault READ canDefault NOTIFY changed)
    Q_PROPERTY(int depth READ depth NOTIFY changed)
    Q_PROPERTY(QQuickItem* page READ page NOTIFY changed)
public:
    explicit KcmHost(QQuickItem *parent=nullptr);
    ~KcmHost() override;
    QString moduleId() const { return m_id; }
    void setModuleId(const QString &id);
    QString error() const { return m_error; }
    bool ready() const;
    bool needsSave() const;
    bool canDefault() const;
    int depth() const;
    QQuickItem *page() const;
    Q_INVOKABLE void save();
    Q_INVOKABLE void reset();
    Q_INVOKABLE void defaults();
    Q_INVOKABLE void back();
    Q_INVOKABLE QStringList availableModules() const;
    Q_INVOKABLE QVariantList catalogue() const;
signals:
    void moduleIdChanged();
    void changed();
    void closeBlocked();
protected:
    void componentComplete() override;
    void geometryChange(const QRectF &newGeometry,const QRectF &oldGeometry) override;
private:
    void load();
    void clear();
    void attach(QQuickItem *item);
    void layout();
    QString m_id,m_error;
    QPointer<KQuickConfigModule> m_module;
    QList<QPointer<QQuickItem>> m_pages;
    QPointer<QQuickWindow> m_window;
    QPointer<WindowCloseGuard> m_guard;
    std::shared_ptr<std::atomic_bool> m_dirty=std::make_shared<std::atomic_bool>(false);
    bool m_complete=false;
};
