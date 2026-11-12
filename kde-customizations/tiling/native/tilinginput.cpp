#include <qqml.h>
#include <QQmlExtensionPlugin>
#include <input.h>
#include <pointer_input.h>
#include <window.h>
#include <QAction>
#include <QVariantMap>

class TilingInput : public QObject {
    Q_OBJECT
public:
    explicit TilingInput(QObject *parent = nullptr) : QObject(parent) {
        auto *action = new QAction(this);
        connect(action, &QAction::triggered, this, [] {
            auto *input = KWin::input();
            if (auto *window = input->pointer()->focus()) {
                window->performMousePressCommand(KWin::Options::MouseUnrestrictedMove,
                                                input->globalPointer());
            }
        });
        KWin::input()->registerPointerShortcut(Qt::MetaModifier | Qt::ShiftModifier,
                                               Qt::LeftButton, action);
    }
    Q_INVOKABLE bool tileGesture() const {
        auto *input = KWin::input();
        if (!input) return false;
        const auto mods = input->keyboardModifiers();
        return mods.testFlag(Qt::MetaModifier) && mods.testFlag(Qt::ShiftModifier)
            && !mods.testFlag(Qt::ControlModifier) && !mods.testFlag(Qt::AltModifier)
            && input->qtButtonStates().testFlag(Qt::LeftButton);
    }
    Q_INVOKABLE QVariantMap requestedGeometry(QObject *client) const {
        const auto *window = qobject_cast<KWin::Window *>(client);
        if (!window || window->isDeleted()) return {};
        const auto r = window->moveResizeGeometry();
        return {{"x", r.x()}, {"y", r.y()}, {"width", r.width()}, {"height", r.height()}};
    }
};

class TilingInputPlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override {
        qmlRegisterType<TilingInput>(uri, 1, 0, "TilingInput");
    }
};
#include "tilinginput.moc"
