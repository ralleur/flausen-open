#include <qqml.h>
#include <QQmlExtensionPlugin>
#include <QAction>
#include <effect/effecthandler.h>

class ScrollBindings : public QObject {
    Q_OBJECT
public:
    explicit ScrollBindings(QObject *parent = nullptr) : QObject(parent) {
        bind(KWin::PointerAxisUp, -1);
        bind(KWin::PointerAxisDown, 1);
    }
private:
    void bind(KWin::PointerAxisDirection axis, int direction) {
        auto *action = new QAction(this);
        connect(action, &QAction::triggered, this, [direction] {
            const auto desktops = KWin::effects->desktops();
            const auto index = desktops.indexOf(KWin::effects->currentDesktop());
            if (index < 0 || desktops.isEmpty()) return;
            KWin::effects->setCurrentDesktop(desktops[(index + direction + desktops.size()) % desktops.size()]);
        });
        KWin::effects->registerAxisShortcut(Qt::MetaModifier, axis, action);
    }
};
class DesktopScrollPlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override {
        qmlRegisterType<ScrollBindings>(uri, 1, 0, "ScrollBindings");
    }
};
#include "desktopscroll.moc"
