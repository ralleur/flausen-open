// SPDX-License-Identifier: MIT
#include "picturepicker.h"
#include <QQuickWindow>
#include <QGuiApplication>
#include <QDBusConnection>
#include <QDBusMessage>
#include <QDBusPendingCallWatcher>
#include <QDBusPendingReply>
#include <QDBusObjectPath>
#include <QDBusArgument>
#include <QDBusMetaType>
#include <QStandardPaths>
#include <QUuid>
#include <KWaylandExtras>
#include <KWindowSystem>

struct PictureFilterEntry { uint kind; QString value; };
using PictureFilterEntries = QList<PictureFilterEntry>;
struct PictureFilter { QString name; PictureFilterEntries entries; };
using PictureFilters = QList<PictureFilter>;
Q_DECLARE_METATYPE(PictureFilterEntry)
Q_DECLARE_METATYPE(PictureFilterEntries)
Q_DECLARE_METATYPE(PictureFilter)
Q_DECLARE_METATYPE(PictureFilters)
QDBusArgument &operator<<(QDBusArgument &a, const PictureFilterEntry &f) { a.beginStructure(); a << f.kind << f.value; a.endStructure(); return a; }
const QDBusArgument &operator>>(const QDBusArgument &a, PictureFilterEntry &f) { a.beginStructure(); a >> f.kind >> f.value; a.endStructure(); return a; }
QDBusArgument &operator<<(QDBusArgument &a, const PictureFilter &f) { a.beginStructure(); a << f.name << f.entries; a.endStructure(); return a; }
const QDBusArgument &operator>>(const QDBusArgument &a, PictureFilter &f) { a.beginStructure(); a >> f.name >> f.entries; a.endStructure(); return a; }
namespace { constexpr auto Service = "org.freedesktop.portal.Desktop"; }
PicturePicker::PicturePicker(QQuickItem *parent) : QQuickItem(parent) {
    qDBusRegisterMetaType<PictureFilterEntry>();
    qDBusRegisterMetaType<PictureFilterEntries>();
    qDBusRegisterMetaType<PictureFilter>();
    qDBusRegisterMetaType<PictureFilters>();
}
PicturePicker::~PicturePicker() { reject(); }
void PicturePicker::open() {
    if (m_open) return;
    m_open = true;
    m_error.clear();
    emit openedChanged();
    if (window() && KWindowSystem::isPlatformWayland()) {
        m_exported = window();
        KWaylandExtras::exportToplevel(window()).then(this, [this](const QString &handle) {
            if (!m_open) return;
            request(handle.isEmpty() ? QString() : QStringLiteral("wayland:") + handle);
        });
    } else {
        request(window() ? QStringLiteral("x11:%1").arg(window()->winId(), 0, 16) : QString());
    }
}
void PicturePicker::request(const QString &parentHandle) {
    const QString token = QStringLiteral("flausen_picture_") + QUuid::createUuid().toString(QUuid::Id128);
    auto bus = QDBusConnection::sessionBus();
    QString sender = bus.baseService().mid(1);
    sender.replace('.', '_');
    m_path = QStringLiteral("/org/freedesktop/portal/desktop/request/%1/%2").arg(sender, token);
    bus.connect(Service, m_path, "org.freedesktop.portal.Request", "Response", this, SLOT(response(uint,QVariantMap,QDBusMessage)));
    PictureFilters filters{{QStringLiteral("Images"), {{1, QStringLiteral("image/*")}}}};
    QVariantMap options{{"handle_token", token}, {"modal", true}, {"multiple", false},
        {"filters", QVariant::fromValue(filters)}, {"accept_label", QStringLiteral("Select")}};
    QByteArray folder = QStandardPaths::writableLocation(QStandardPaths::PicturesLocation).toUtf8();
    folder.append('\0');
    options.insert("current_folder", folder);
    auto call = QDBusMessage::createMethodCall(Service, "/org/freedesktop/portal/desktop", "org.freedesktop.portal.FileChooser", "OpenFile");
    call << parentHandle << QStringLiteral("Choose a profile picture") << options;
    auto watcher = new QDBusPendingCallWatcher(bus.asyncCall(call), this);
    connect(watcher, &QDBusPendingCallWatcher::finished, this, [this, watcher] {
        QDBusPendingReply<QDBusObjectPath> reply = *watcher;
        watcher->deleteLater();
        if (reply.isError()) { if (m_open) fail(reply.error().message()); return; }
        const QString path = reply.value().path();
        if (!m_open) {
            QDBusConnection::sessionBus().asyncCall(QDBusMessage::createMethodCall(Service, path, "org.freedesktop.portal.Request", "Close"));
        } else if (path != m_path) {
            QDBusConnection::sessionBus().disconnect(Service, m_path, "org.freedesktop.portal.Request", "Response", this, nullptr);
            m_path = path;
            QDBusConnection::sessionBus().connect(Service, m_path, "org.freedesktop.portal.Request", "Response", this, SLOT(response(uint,QVariantMap,QDBusMessage)));
        }
    });
}
void PicturePicker::response(uint code, const QVariantMap &results, const QDBusMessage &message) {
    if (!m_open || message.path() != m_path) return;
    const auto uris = results.value("uris").toStringList();
    finish();
    if (code == 0 && !uris.isEmpty()) {
        const QUrl selected(uris.first());
        if (!selected.isLocalFile()) { fail(QStringLiteral("Please select a local image file.")); return; }
        m_selected = selected;
        emit accepted();
    } else if (code != 1) fail(QStringLiteral("Could not complete image selection."));
}
void PicturePicker::reject() {
    if (!m_path.isEmpty()) QDBusConnection::sessionBus().asyncCall(QDBusMessage::createMethodCall(Service, m_path, "org.freedesktop.portal.Request", "Close"));
    finish();
}
void PicturePicker::finish() {
    if (!m_path.isEmpty()) QDBusConnection::sessionBus().disconnect(Service, m_path, "org.freedesktop.portal.Request", "Response", this, nullptr);
    m_path.clear();
    if (m_exported) KWaylandExtras::unexportToplevel(m_exported);
    m_exported.clear();
    if (m_open) { m_open = false; emit openedChanged(); }
}
void PicturePicker::fail(const QString &message) {
    finish();
    m_error = QStringLiteral("Could not open the KDE image picker. ") + message;
    emit failed();
}
