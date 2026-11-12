// SPDX-License-Identifier: MIT
#include "dialogstyle.h"
#include <QStyleFactory>
#include <QStylePlugin>
#include <QSettings>
#include <QStandardPaths>
class Plugin : public QStylePlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QStyleFactoryInterface_iid FILE "plugin.json")
public:
    QStyle *create(const QString &key) override {
        if (key.compare("ralleur-dialogs", Qt::CaseInsensitive)) return nullptr;
        QSettings config(QStandardPaths::writableLocation(QStandardPaths::GenericConfigLocation)
            + "/ralleur-dialogs.ini", QSettings::IniFormat);
        auto base = config.value("BaseStyle", "darkly").toString();
        if (base.compare("ralleur-dialogs", Qt::CaseInsensitive) == 0) base = "Breeze";
        auto style = QStyleFactory::create(base);
        if (!style) style = QStyleFactory::create("Fusion");
        return new RalleurDialogStyle(style);
    }
};
#include "plugin.moc"
