// SPDX-License-Identifier: MIT
#pragma once
#include <QObject>
#include <QJsonObject>
#include <QFileSystemWatcher>
#include <QFutureWatcher>
#include <QHash>
#include <QTimer>
#include <QUrl>

class KUrlNavigator;

namespace Ralleur {
QString directoryIdentity(const QString &path);
QString colorForIcon(const QString &icon);

class FolderPolicy {
public:
    QJsonObject data;
    QString home() const;
    QString colorForPath(const QString &path) const;
    bool valid() const;
    static FolderPolicy load(const QString &file);
};

// Uses KDE's standard .directory/Icon setting, so KIO's ordinary folder
// thumbnails and other KDE file views see the same color as Dolphin.
QList<QUrl> applyFolderColors(const FolderPolicy &policy, const QString &directory,
                             const QString &journalDirectory);

class FolderColors : public QObject {
    Q_OBJECT
public:
    FolderColors(FolderPolicy policy, QString journalDirectory, QObject *parent = nullptr);
    void bind(KUrlNavigator *navigator);
    void watchPath(QObject *source, const QString &path);
private:
    void refreshWatches();
    void schedule();
    void update();
    FolderPolicy m_policy;
    QString m_journal;
    QHash<QObject *, QString> m_paths;
    QFileSystemWatcher m_watch;
    QTimer m_delay;
    QFutureWatcher<QList<QUrl>> m_future;
    bool m_again = false;
};
}
