// SPDX-License-Identifier: MIT
// Explicit test plugin, never installed by the normal wrapper.
#include <QApplication>
#include <QGenericPlugin>
#include <QTimer>
#include <QWidget>
#include <QMenu>
#include <QKeyEvent>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QPointer>

class ContextProbe : public QGenericPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QGenericPluginFactoryInterface_iid FILE "live_context_probe.json")
public:
    static void writePoolState(const QString &path) {
        QJsonArray passes;
        int active = 0;
        for (auto pass : QApplication::topLevelWidgets()) {
            if (pass->objectName() != QStringLiteral("ralleurContextBlurPass")) continue;
            active += pass->property("ralleurContextBlurActive").toBool();
            passes.append(QJsonObject{{"width", pass->width()}, {"height", pass->height()},
                                     {"visible", pass->isVisible()}});
        }
        QFile file(path);
        if (file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(QJsonObject{{"active", active}, {"passes", passes}}).toJson());
    }
    QObject *create(const QString &key, const QString &) override {
        const auto output = qEnvironmentVariable("RALLEUR_CONTEXT_PROBE_DIR");
        if (key != "ralleurcontextprobe" || output.isEmpty()) return nullptr;
        auto lifetime = new QObject;
        QTimer::singleShot(1800, lifetime, [output, lifetime] {
            QWidget *window = nullptr, *view = nullptr;
            for (auto w : QApplication::topLevelWidgets()) if (w->inherits("DolphinMainWindow")) window = w;
            if (window) for (auto w : window->findChildren<QWidget *>())
                if (w->inherits("DolphinView") && w->isVisible()) { view = w; break; }
            if (!view) { qApp->exit(2); return; }
            QFile info(output + "/probe-info.json");
            if (info.open(QIODevice::WriteOnly)) info.write(QJsonDocument(QJsonObject{
                {"platform", QGuiApplication::platformName()}, {"header", bool(window->findChild<QObject *>("ralleurHeader"))},
                {"libraryPaths", QJsonArray::fromStringList(QCoreApplication::libraryPaths())}}).toJson());
            QMetaObject::invokeMethod(view, "selectAll", Qt::DirectConnection);
            const bool nativeInput = qEnvironmentVariableIsSet("RALLEUR_CONTEXT_PROBE_NATIVE_INPUT");
            QTimer::singleShot(nativeInput ? 4000 : 700, lifetime, [output, lifetime, window] {
                for (auto widget : QApplication::topLevelWidgets()) {
                    auto menu = qobject_cast<QMenu *>(widget);
                    if (!menu || !menu->isVisible() || !menu->inherits("DolphinContextMenu")) continue;
                    menu->grab().save(output + "/menu.png");
                    QJsonObject report{{"visible", true}, {"glass", menu->property("ralleurGlassMenu").toBool()},
                        {"translucent", menu->testAttribute(Qt::WA_TranslucentBackground)}, {"style", menu->styleSheet()},
                        {"x", menu->x()}, {"y", menu->y()}, {"width", menu->width()}, {"height", menu->height()}};
                    QJsonArray entries;
                    QJsonArray blurPasses;
                    for (auto pass : QApplication::topLevelWidgets()) {
                        if (pass->objectName() != QStringLiteral("ralleurContextBlurPass")) continue;
                        blurPasses.append(QJsonObject{{"active", pass->property("ralleurContextBlurActive").toBool()},
                            {"visible", pass->isVisible()}, {"x", pass->x()}, {"y", pass->y()},
                            {"width", pass->width()}, {"height", pass->height()}});
                    }
                    report["blurPasses"] = blurPasses;
                    for (auto action : menu->actions()) entries.append(QJsonObject{{"text", action->text()}, {"icon", action->icon().name()}});
                    report["entries"] = entries;
                    for (auto action : menu->actions()) if (action->objectName() == "ralleurZip") {
                        report["zipDirect"] = !action->menu();
                        QPointer<QMenu> guard(menu);
                        QTimer::singleShot(2200, lifetime, [guard, action, output] {
                            if (!guard) return;
                            QKeyEvent press(QEvent::KeyPress, Qt::Key_Shift, Qt::ShiftModifier);
                            QApplication::sendEvent(guard, &press);
                            if (auto options = action->menu()) {
                                options->popup(guard->mapToGlobal(QPoint(guard->width(), guard->actionGeometry(action).top())));
                                QTimer::singleShot(500, options, [options, output] {
                                    options->grab().save(output + "/submenu.png");
                                    writePoolState(output + "/submenu-pool.json");
                                });
                            }
                        });
                    }
                    QFile file(output + "/report.json");
                    if (file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(report).toJson());
                    QTimer::singleShot(9000, lifetime, [menu, window, output] {
                        menu->close();
                        writePoolState(output + "/closed-pool.json");
                        window->close(); qApp->quit();
                    });
                    return;
                }
                qApp->exit(3);
            });
            const auto pos = view->mapToGlobal(QPoint(280, 150));
            if (nativeInput) {
                QFile file(output + "/click.json");
                if (file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(QJsonObject{
                    {"x", pos.x()}, {"y", pos.y()}, {"localX", view->mapTo(window, QPoint(280, 150)).x()},
                    {"localY", view->mapTo(window, QPoint(280, 150)).y()}, {"pid", QCoreApplication::applicationPid()}}).toJson());
            } else {
                QMetaObject::invokeMethod(view, "slotItemContextMenuRequested", Qt::DirectConnection,
                                          Q_ARG(int, 0), Q_ARG(QPointF, QPointF(pos)));
            }
        });
        return lifetime;
    }
};
#include "live_context_probe.moc"
