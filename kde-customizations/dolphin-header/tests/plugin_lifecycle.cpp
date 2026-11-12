// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QMainWindow>
#include <QTemporaryDir>
#include <QTimer>
#include <QToolBar>
#include <QWindow>

class DolphinMainWindow : public QMainWindow {
    Q_OBJECT
public:
    DolphinMainWindow() {
        setObjectName("Dolphin_Lifecycle");
        addToolBar("Main")->setObjectName("mainToolBar");
        resize(900, 460);
    }
};

int main(int argc, char **argv) {
    QTemporaryDir isolated;
    qputenv("XDG_CONFIG_HOME", (isolated.path()+"/config").toLocal8Bit());
    qputenv("XDG_DATA_HOME", (isolated.path()+"/data").toLocal8Bit());
    QApplication app(argc, argv);
    DolphinMainWindow window;
    window.show();
    QTimer::singleShot(50, &app, [&] {
        if (!window.findChild<QObject *>("ralleurHeader")
            || window.windowHandle()->format().alphaBufferSize() != 8
            || qEnvironmentVariable("QT_QPA_GENERIC_PLUGINS").contains("ralleurdolphin")
            || qEnvironmentVariableIsSet("RALLEUR_DOLPHIN_PLUGIN_DIR")) {
            app.exit(2);
            return;
        }
        window.close();
    });
    QTimer::singleShot(1000, &app, [&] { app.exit(3); });
    return app.exec();
}
#include "plugin_lifecycle.moc"
