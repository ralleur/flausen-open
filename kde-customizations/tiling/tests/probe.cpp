#include <qqml.h>
#include <QQmlExtensionPlugin>
#include <QDBusConnection>
#include <QVariantMap>
#include <QQmlEngine>
#include <QJSValue>
#include <QJsonDocument>
#include <QQmlComponent>
#include <workspace.h>
#include <outline.h>
#include <input.h>
#include <window.h>

class Probe : public QObject {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.ralleur.TilingProbe")
public:
    mutable bool watching = false;
    mutable QStringList warnings;
    explicit Probe(QObject *parent = nullptr) : QObject(parent) {
        QDBusConnection::sessionBus().registerObject("/RalleurTilingProbe", this,
                                                   QDBusConnection::ExportScriptableSlots);
    }
    ~Probe() override {
        QDBusConnection::sessionBus().unregisterObject("/RalleurTilingProbe");
    }
public Q_SLOTS:
    Q_SCRIPTABLE QVariantMap inspect() const {
        if (!watching) {
            watching = true;
            connect(qmlEngine(this), &QQmlEngine::warnings, this, [this](const QList<QQmlError> &errors) {
                for (const auto &error : errors) warnings.append(error.toString());
            });
        }
        auto *window = KWin::workspace()->moveResizeWindow();
        QVariantMap result{{"outline", KWin::workspace()->outline()->isActive()},
                {"shift", KWin::input()->keyboardModifiers().testFlag(Qt::ShiftModifier)},
                {"moving", window && window->isInteractiveMove()}};
        if (window) {
            result["caption"] = window->caption();
            result["width"] = window->frameGeometry().width();
            result["height"] = window->frameGeometry().height();
        }
        const auto objects = qmlEngine(this)->parent()->findChildren<QObject *>();
        for (QObject *object : objects) {
            if (object->objectName() != "ralleur-drop-indicator") continue;
            result["previewVisible"] = object->property("visible").toBool() && object->property("indicatorReady").toBool();
            // A hidden preview may have an undefined/null target. QtDBus cannot
            // marshal an invalid QVariant inside a{sv} and aborts the compositor.
            const auto target = object->property("targetGeometry").value<QJSValue>().toVariant();
            if (target.isValid() && !target.isNull()) result["previewTarget"] = target;
            result["previewLabel"] = object->property("actionLabel").toString();
        }
        QStringList componentErrors;
        for (auto *component : qmlEngine(this)->parent()->findChildren<QQmlComponent *>()) {
            for (const auto &error : component->errors()) componentErrors.append(error.toString());
        }
        result["errors"] = componentErrors + warnings;
        return result;
    }
    Q_SCRIPTABLE QVariantMap checkpoint() const {
        auto *engine = qmlEngine(this);
        QStringList roots;
        for (QObject *object : engine->parent()->findChildren<QObject *>()) {
            if (object->metaObject()->indexOfProperty("runtime") < 0) continue;
            const auto runtime = object->property("runtime").value<QJSValue>();
            roots.append(QString::fromLatin1(object->metaObject()->className()) + ":" + runtime.toString() + ":driver=" + runtime.property("driver").toString());
            if (!runtime.isObject() || !runtime.property("driver").isObject()) continue;
            auto capture = engine->evaluate(QStringLiteral(R"JS((function(runtime) {
                const d=runtime.driver, e=d.engine;
                const windows=e.windows.list.map(w=>({id:w.id,tiled:w.isTiled,
                    floatGeometry:w.ralleurFloatGeometry || w.floatGeometry}));
                const layouts=[], seen=new Set();
                for(const w of e.windows.list) {
                    if(seen.has(w.surface.id)) continue;
                    seen.add(w.surface.id);
                    const l=e.layouts.getCurrentLayout(w.surface);
                    if(l.vsplit!==undefined) layouts.push({windowId:w.id,vsplit:l.vsplit,lhsplit:l.lhsplit,rhsplit:l.rhsplit});
                }
                return JSON.parse(JSON.stringify({windows,layouts}));
            }))JS"));
            return capture.call({runtime}).toVariant().toMap();
        }
        QStringList errors;
        for (auto *component : engine->parent()->findChildren<QQmlComponent *>()) {
            for (const auto &error : component->errors()) errors.append(error.toString());
        }
        return {{"error", "No active Krohnkite runtime found"}, {"componentErrors", errors}, {"roots", roots}};
    }
    Q_SCRIPTABLE bool restoreCheckpoint(const QString &payload) {
        for (QObject *object : qmlEngine(this)->parent()->findChildren<QObject *>()) {
            if (object->metaObject()->indexOfProperty("runtime") < 0) continue;
            if (object->metaObject()->indexOfMethod("restoreRalleurCheckpoint(QVariant)") < 0) continue;
            return QMetaObject::invokeMethod(object, "restoreRalleurCheckpoint", Q_ARG(QVariant, payload));
        }
        return false;
    }
};
class ProbePlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override { qmlRegisterType<Probe>(uri, 1, 0, "Probe"); }
};
#include "probe.moc"
