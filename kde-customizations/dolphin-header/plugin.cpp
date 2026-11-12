// SPDX-License-Identifier: MIT
#include "header.h"
#include <QCoreApplication>
#include <QFileInfo>
#include <QGenericPlugin>
#include <QTimer>

class DolphinHeaderPlugin : public QGenericPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QGenericPluginFactoryInterface_iid FILE "plugin.json")
public:
    QObject *create(const QString &key, const QString &) override
    {
        const auto application = QFileInfo(QCoreApplication::applicationFilePath()).fileName();
        if (key.compare(QStringLiteral("ralleurdolphin"), Qt::CaseInsensitive) != 0
            || (application != QStringLiteral("dolphin") && application != QStringLiteral("xdg-desktop-portal-kde")))
            return nullptr;
        // The factory runs during QGuiApplication construction. QWidget APIs are
        // used only once QApplication and Dolphin have finished constructing.
        // QGuiApplication owns generic-plugin instances separately from its
        // QObject children. Giving this a qApp parent would delete it twice
        // during application teardown.
        auto integration = new Ralleur::Integration;
        QTimer::singleShot(0, integration, &Ralleur::Integration::start);
        return integration;
    }
};
#include "plugin.moc"
