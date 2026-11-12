#include <qqml.h>
#include <QQmlExtensionPlugin>
#include <input.h>
#include <input_event.h>
#include <workspace.h>
#include <window.h>
#include <KConfigGroup>
#include <KConfigWatcher>
#include <KSharedConfig>
#include <QTimer>

// Run after lockscreen/effects and before KWin's InteractiveMoveResize filter.
// Keep the real keyboard state intact so Krohnkite still sees Meta+Shift.
class ShiftDragFilter : public QObject, public KWin::InputEventFilter {
public:
    ShiftDragFilter() : InputEventFilter(KWin::InputFilterOrder::Effects) {}
    bool enabled = false;

    KWin::Window *movingWindow() const {
        auto *window = KWin::workspace()->moveResizeWindow();
        return enabled && window && window->isInteractiveMove() ? window : nullptr;
    }
    bool pointerMotion(KWin::PointerMotionEvent *event) override {
        if (movingWindow() && event->buttons.testFlag(Qt::LeftButton)) {
            event->modifiers &= ~Qt::ShiftModifier;
        } else if (enabled && event->buttons.testFlag(Qt::LeftButton)) {
            // Decoration drags can start later in this very event, after this
            // filter. Sanitize that first update before the next rendered frame.
            QTimer::singleShot(0, this, [this] {
                if (auto *window = movingWindow()) {
                    window->updateInteractiveMoveResize(KWin::input()->globalPointer(),
                        KWin::input()->keyboardModifiers() & ~Qt::ShiftModifier);
                }
            });
        }
        return false;
    }
    bool pointerButton(KWin::PointerButtonEvent *event) override {
        if (auto *window = movingWindow()) {
            // KWin reads the stored drag modifiers when the last button is released.
            window->updateInteractiveMoveResize(event->position, event->modifiers & ~Qt::ShiftModifier);
        }
        return false;
    }
    bool keyboardKey(KWin::KeyboardKeyEvent *event) override {
        auto *window = movingWindow();
        if (!window || !KWin::input()->qtButtonStates().testFlag(Qt::LeftButton)) return false;
        // Mirror KWin's move filter with sanitized drag modifiers. In particular,
        // pressing Shift after the drag starts must not re-enable the native grid.
        const auto mods = event->modifiers & ~Qt::ShiftModifier;
        if (event->state == KWin::KeyboardKeyState::Pressed ||
            event->state == KWin::KeyboardKeyState::Repeated) {
            window->keyPressEvent(QKeyCombination{mods, event->key});
            if (window->isInteractiveMove()) {
                window->updateInteractiveMoveResize(KWin::input()->globalPointer(), mods);
            }
        }
        return true;
    }
};

class TilingShiftGuard : public QObject {
    Q_OBJECT
public:
    explicit TilingShiftGuard(QObject *parent = nullptr) : QObject(parent) {
        config = KSharedConfig::openConfig(QStringLiteral("kwinrc"));
        watcher = KConfigWatcher::create(config);
        connect(watcher.data(), &KConfigWatcher::configChanged, this, [this] { refresh(); });
        refresh();
        KWin::input()->installInputEventFilter(&filter);
    }
private:
    void refresh() {
        config->reparseConfiguration();
        filter.enabled = config->group(QStringLiteral("Plugins"))
                             .readEntry("krohnkiteEnabled", false);
    }
    KSharedConfig::Ptr config;
    KConfigWatcher::Ptr watcher;
    ShiftDragFilter filter;
};

class TilingShiftGuardPlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override {
        qmlRegisterType<TilingShiftGuard>(uri, 1, 0, "TilingShiftGuard");
    }
};
#include "shiftguard.moc"
