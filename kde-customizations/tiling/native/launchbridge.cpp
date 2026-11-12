#include <QQmlExtensionPlugin>
#include <qqml.h>
#include <QDBusConnection>
#include <QJsonDocument>
#include <QJsonArray>

// The session-local endpoint is owned by the active Krohnkite component.
class LaunchBridge : public QObject {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.ralleur.TilingLaunch")
public:
    explicit LaunchBridge(QObject *parent = nullptr) : QObject(parent) {
        registered = QDBusConnection::sessionBus().registerObject(
            "/RalleurTilingLaunch", this, QDBusConnection::ExportScriptableSlots);
    }
    ~LaunchBridge() override {
        if (registered) QDBusConnection::sessionBus().unregisterObject("/RalleurTilingLaunch");
    }
public slots:
    Q_SCRIPTABLE bool arm(const QString &payload) {
        const auto doc = QJsonDocument::fromJson(payload.toUtf8());
        if (!doc.isArray() || doc.array().isEmpty() || doc.array().size() > 16) return false;
        for (const auto &value : doc.array()) {
            if (!value.isString() || value.toString().isEmpty() || value.toString().size() > 256) return false;
        }
        emit requested(payload);
        return true;
    }
signals:
    void requested(const QString &payload);
private:
    bool registered = false;
};
class LaunchBridgePlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override { qmlRegisterType<LaunchBridge>(uri, 1, 0, "LaunchBridge"); }
};
#include "launchbridge.moc"
