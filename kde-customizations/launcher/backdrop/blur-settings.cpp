// SPDX-License-Identifier: MIT
// Single-process equivalent of blur-strength.py, sharing its locked lease files.
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QSaveFile>
#include <QSet>
#include <QDBusConnection>
#include <QDBusMessage>
#include <KSharedConfig>
#include <KConfigGroup>
#include <sys/file.h>
#include <unistd.h>

static QJsonDocument readJson(const QString &path) {
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) return {};
    return QJsonDocument::fromJson(file.readAll());
}
static bool saveJson(const QString &path, const QJsonDocument &data) {
    QSaveFile file(path);
    const QByteArray bytes = data.toJson(QJsonDocument::Compact);
    return file.open(QIODevice::WriteOnly) && file.write(bytes) == bytes.size() && file.commit();
}
int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    const auto args = app.arguments();
    if (args.size() < 2) return 2;
    const QString action = args[1];
    if (action != "on" && action != "off" && action != "off-launchers") return 2;
    const QString owner = args.value(2, "polkit");
    const QString runtime = qEnvironmentVariable("XDG_RUNTIME_DIR", "/run/user/" + QString::number(getuid()));
    const QString dir = runtime + "/minimal-polkit";
    QDir().mkpath(dir);
    QFile lock(dir + "/lock");
    if (!lock.open(QIODevice::ReadWrite) || flock(lock.handle(), LOCK_EX)) return 3;
    const QString saved = dir + "/blur-settings.json", leases = dir + "/blur-owners.json";
    QSet<QString> owners;
    if (QFile::exists(leases)) {
        for (const auto &value : readJson(leases).array()) owners.insert(value.toString());
    } else if (QFile::exists(saved)) owners.insert("polkit");
    if (action == "on") owners.insert(owner);
    else if (action == "off") owners.remove(owner);
    else for (const auto &value : QSet<QString>(owners)) if (value.startsWith("launcher:")) owners.remove(value);
    auto config = KSharedConfig::openConfig("kwinrc", KConfig::NoGlobals);
    KConfigGroup group(config, "Effect-blur");
    QJsonObject desired;
    const QStringList keys = {"BlurStrength", "NoiseStrength", "Saturation"};
    if (!owners.isEmpty()) {
        if (!QFile::exists(saved)) {
            QJsonObject previous;
            for (const auto &key : keys) previous[key] = group.readEntry(key, QString("__unset__"));
            if (!saveJson(saved, QJsonDocument(previous))) return 4;
        }
        desired = {{"BlurStrength", "1"}, {"NoiseStrength", "0"}, {"Saturation", "100"}};
    } else if (QFile::exists(saved)) desired = readJson(saved).object();
    bool changed = false;
    for (auto it = desired.begin(); it != desired.end(); ++it) {
        const QString value = it.value().toString();
        if (group.readEntry(it.key(), QString("__unset__")) == value) continue;
        if (value == "__unset__") group.deleteEntry(it.key());
        else group.writeEntry(it.key(), value);
        changed = true;
    }
    if (changed) {
        if (!config->sync()) return 5;
        auto call = QDBusMessage::createMethodCall("org.kde.KWin", "/Effects", "org.kde.kwin.Effects", "reconfigureEffect");
        call << QString("blur");
        if (QDBusConnection::sessionBus().call(call).type() == QDBusMessage::ErrorMessage) return 6;
    }
    if (!owners.isEmpty()) {
        QStringList sorted(owners.begin(), owners.end()); sorted.sort();
        if (!saveJson(leases, QJsonDocument(QJsonArray::fromStringList(sorted)))) return 7;
    } else { QFile::remove(saved); QFile::remove(leases); }
    return 0;
}
