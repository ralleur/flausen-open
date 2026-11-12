// SPDX-License-Identifier: MIT
#include "foldercolors.h"
#include <KConfig>
#include <KConfigGroup>
#include <KFileItem>
#include <KUrlNavigator>
#include <KDirNotify>
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QLockFile>
#include <QSaveFile>
#include <QtConcurrent>
#include <sys/stat.h>

namespace Ralleur {
namespace {
QString canonical(const QString &path) { return QFileInfo(path).canonicalFilePath(); }
QString hash(const QByteArray &bytes) { return QString::fromLatin1(QCryptographicHash::hash(bytes, QCryptographicHash::Sha256).toHex()); }
QByteArray read(const QString &file) { QFile f(file); return f.open(QIODevice::ReadOnly) ? f.readAll() : QByteArray(); }
bool save(const QString &file, const QByteArray &bytes) {
    QSaveFile f(file);
    return f.open(QIODevice::WriteOnly) && f.write(bytes) == bytes.size() && f.commit();
}
QString directoryIcon(const QString &path) {
    KConfig config(path + QStringLiteral("/.directory"), KConfig::SimpleConfig);
    return KConfigGroup(&config, "Desktop Entry").readEntry("Icon", QString());
}
bool isInside(const QString &path, const QString &home) {
    return path == home || path.startsWith(home + '/');
}
bool vcsInternal(const QString &path) {
    const auto components = path.split('/');
    return components.contains(".git") || components.contains(".hg") || components.contains(".svn");
}
}

QString directoryIdentity(const QString &path) {
    struct stat info;
    if (::stat(QFile::encodeName(path).constData(), &info) != 0) return {};
    return QString::number(quint64(info.st_dev)) + ':' + QString::number(quint64(info.st_ino));
}

QString colorForIcon(const QString &icon) {
    static const QHash<QString, QString> colors = {
        {"inode-directory", "red"}, {"folder", "red"}, {"folder-open", "red"},
        {"folder-red", "red"}, {"folder-download", "red"},
        {"folder-blue", "blue"}, {"folder-documents", "blue"}, {"folder-videos", "blue"},
        {"folder-desktop", "blue"}, {"user-desktop", "blue"},
        {"folder-yellow", "yellow"}, {"folder-templates", "yellow"},
        {"folder-green", "green"}, {"folder-music", "green"},
        {"folder-violet", "violet"}, {"folder-pictures", "violet"},
        {"folder-grey", "grey"}, {"folder-public", "grey"}, {"folder-downloads", "grey"},
        {"folder-cyan", "cyan"}, {"folder-orange", "orange"}
    };
    return colors.value(QFileInfo(icon).completeBaseName());
}

QString FolderPolicy::home() const { return data.value("home").toString(); }
bool FolderPolicy::valid() const { return !home().isEmpty() && data.value("version").toInt() == 1; }
FolderPolicy FolderPolicy::load(const QString &file) { return {QJsonDocument::fromJson(read(file)).object()}; }

QString FolderPolicy::colorForPath(const QString &path) const {
    const auto real = canonical(path);
    if (real.isEmpty() || !isInside(real, home())) return data.value("outsideHomeColor").toString("red");
    if (real == home()) return data.value("defaultHomeColor").toString("yellow");
    const auto name = real.mid(home().size() + 1).section('/', 0, 0);
    const auto root = home() + '/' + name;
    // A color explicitly chosen on a Home category overrides the snapshot.
    const auto explicitColor = colorForIcon(directoryIcon(root));
    if (!explicitColor.isEmpty()) return explicitColor;
    const auto identity = directoryIdentity(root);
    for (const auto &entry : data.value("roots").toArray()) {
        const auto object = entry.toObject();
        if (object.value("id").toString() == identity) {
            const auto oldColor = colorForIcon(object.value("icon").toString());
            return oldColor.isEmpty() ? QStringLiteral("red") : oldColor;
        }
    }
    return data.value("defaultHomeColor").toString("yellow");
}

QList<QUrl> applyFolderColors(const FolderPolicy &policy, const QString &directory, const QString &journalDirectory) {
    QList<QUrl> changed;
    if (!policy.valid() || !QFileInfo(directory).isDir()) return changed;
    const auto entries = QDir(directory).entryInfoList(QDir::Dirs | QDir::Hidden | QDir::NoDotAndDotDot | QDir::NoSymLinks);
    for (const auto &entry : entries) {
        const auto path = entry.canonicalFilePath();
        if (path.isEmpty() || path == policy.home() || vcsInternal(path)) continue;
        const auto color = policy.colorForPath(path);
        const auto current = KFileItem(QUrl::fromLocalFile(path)).iconName();
        const auto currentColor = colorForIcon(current);
        // Preserve non-folder application/device icons; red default folders
        // already satisfy the outside-Home rule without filesystem writes.
        if (currentColor.isEmpty() || currentColor == color || !entry.isWritable()) continue;
        const auto metadata = path + QStringLiteral("/.directory");
        const QFileInfo metaInfo(metadata);
        if (metaInfo.isSymLink() || (metaInfo.exists() && (!metaInfo.isWritable() || metaInfo.size() > 131072))) continue;
        QDir().mkpath(journalDirectory);
        const auto recordPath = journalDirectory + '/' + hash(directoryIdentity(path).toUtf8()) + QStringLiteral(".json");
        QLockFile lock(recordPath + QStringLiteral(".lock"));
        if (!lock.tryLock(0)) continue;
        const auto original = read(metadata);
        auto record = QJsonDocument::fromJson(read(recordPath)).object();
        if (!record.isEmpty() && record.value("lastDigest").toString() != hash(original)) continue;
        if (record.isEmpty()) {
            struct stat metadataStat;
            const int mode = ::stat(QFile::encodeName(metadata).constData(), &metadataStat) == 0 ? metadataStat.st_mode & 07777 : 0;
            record = {{"identity", directoryIdentity(path)}, {"existedBefore", metaInfo.exists()},
                {"before", QString::fromLatin1(original.toBase64())}, {"mode", mode}};
        }
        record["path"] = metadata;
        record["lastDigest"] = hash(original);
        // Save original bytes before making the reversible metadata change.
        if (!save(recordPath, QJsonDocument(record).toJson())) continue;
        KConfig config(metadata, KConfig::SimpleConfig);
        KConfigGroup(&config, "Desktop Entry").writeEntry("Icon", QStringLiteral("folder-") + color);
        if (!config.sync()) continue;
        record["lastDigest"] = hash(read(metadata));
        save(recordPath, QJsonDocument(record).toJson());
        changed.append(QUrl::fromLocalFile(path));
    }
    return changed;
}

FolderColors::FolderColors(FolderPolicy policy, QString journalDirectory, QObject *parent)
    : QObject(parent), m_policy(std::move(policy)), m_journal(std::move(journalDirectory)) {
    m_delay.setSingleShot(true);
    m_delay.setInterval(80);
    connect(&m_delay, &QTimer::timeout, this, &FolderColors::update);
    connect(&m_watch, &QFileSystemWatcher::directoryChanged, this, [this] { schedule(); });
    connect(&m_future, &QFutureWatcher<QList<QUrl>>::finished, this, [this] {
        const auto changed = m_future.result();
        if (!changed.isEmpty()) org::kde::KDirNotify::emitFilesChanged(changed);
        if (m_again) { m_again = false; schedule(); }
    });
    refreshWatches();
    schedule();
}

void FolderColors::bind(KUrlNavigator *navigator) {
    if (!m_policy.valid() || navigator->property("ralleurFolderColors").toBool()) return;
    navigator->setProperty("ralleurFolderColors", true);
    connect(navigator, &KUrlNavigator::urlChanged, this, [this, navigator](const QUrl &url) {
        watchPath(navigator, url.isLocalFile() ? url.toLocalFile() : QString());
    });
    connect(navigator, &QObject::destroyed, this, [this, navigator] {
        m_paths.remove(navigator); refreshWatches();
    });
    const auto url = navigator->locationUrl();
    watchPath(navigator, url.isLocalFile() ? url.toLocalFile() : QString());
}

void FolderColors::watchPath(QObject *source, const QString &path) {
    if (!m_policy.valid()) return;
    m_paths[source] = canonical(path);
    refreshWatches(); schedule();
}

void FolderColors::refreshWatches() {
    if (!m_policy.valid()) return;
    QSet<QString> paths{m_policy.home()};
    for (const auto &path : m_paths) {
        if (path.isEmpty()) continue;
        paths.insert(path);
        if (path.startsWith(m_policy.home() + '/'))
            paths.insert(m_policy.home() + '/' + path.mid(m_policy.home().size()+1).section('/', 0, 0));
    }
    const auto watched = m_watch.directories();
    const QSet<QString> old(watched.begin(), watched.end());
    for (const auto &path : old) if (!paths.contains(path)) m_watch.removePath(path);
    for (const auto &path : paths) if (!old.contains(path) && QFileInfo(path).isDir()) m_watch.addPath(path);
}
void FolderColors::schedule() { if (m_policy.valid()) m_delay.start(); }
void FolderColors::update() {
    if (m_future.isRunning()) { m_again = true; return; }
    QSet<QString> directories{m_policy.home()};
    for (const auto &path : m_paths) if (!path.isEmpty()) directories.insert(path);
    const auto policy = m_policy;
    const auto journal = m_journal;
    m_future.setFuture(QtConcurrent::run([policy, journal, directories] {
        QList<QUrl> changes;
        for (const auto &path : directories) changes.append(applyFolderColors(policy, path, journal));
        return changes;
    }));
}
}
