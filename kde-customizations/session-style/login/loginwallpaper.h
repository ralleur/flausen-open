/*
 * Based on Plasma Login Manager's wallpaperapp.cpp (KDE, GPL-2.0-or-later).
 * Loads the same configured wallpaper into the greeter's scene so the shared
 * lock/login card can sample it for local backdrop blur.
 * SPDX-License-Identifier: GPL-2.0-or-later
 */
#pragma once
#include <QFile>
#include <QQmlComponent>
#include <QQuickView>
#include <QQuickItem>
#include <KConfigLoader>
#include <KConfigPropertyMap>
#include <KPackage/PackageLoader>
#include "plasmaloginsettings.h"

inline void loadRalleurLoginWallpaper(QQuickView *window)
{
    if (!window->rootObject()) return;
    auto container = window->rootObject()->property("wallpaperContainer").value<QQuickItem *>();
    if (!container) return;
    auto &settings = PlasmaLoginSettings::getInstance();
    auto package = KPackage::PackageLoader::self()->loadPackage(QStringLiteral("Plasma/Wallpaper"));
    package.setPath(settings.wallpaperPluginId());
    if (!package.isValid()) {qWarning() << "Ralleur: wallpaper package unavailable"; return;}
    const auto cfg = settings.sharedConfig()->group(QStringLiteral("Greeter"))
        .group(QStringLiteral("Wallpaper")).group(settings.wallpaperPluginId());
    const auto xml = package.filePath("config", QStringLiteral("main.xml"));
    KConfigLoader *loader;
    if (xml.isEmpty()) loader = new KConfigLoader(cfg, nullptr, window);
    else {QFile file(xml); loader = new KConfigLoader(cfg, &file, window);}
    auto config = new KConfigPropertyMap(loader, window);
    config->setNotify(true);
    QQmlComponent component(window->engine(), QUrl::fromLocalFile(package.filePath("mainscript")), window);
    const QVariantMap properties{{QStringLiteral("configuration"), QVariant::fromValue(config)},
        {QStringLiteral("pluginName"), settings.wallpaperPluginId()}};
    auto object = component.createWithInitialProperties(properties, window->rootContext());
    auto item = qobject_cast<QQuickItem *>(object);
    if (!item) {qWarning() << "Ralleur: wallpaper creation failed" << component.errors(); delete object; return;}
    item->setParent(window);
    item->setParentItem(container);
    item->setSize(container->size());
    QObject::connect(container, &QQuickItem::widthChanged, item, [container,item] {item->setWidth(container->width());});
    QObject::connect(container, &QQuickItem::heightChanged, item, [container,item] {item->setHeight(container->height());});
}
