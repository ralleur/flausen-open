// SPDX-License-Identifier: MIT
// Installer helper: ask the installed KIO for its defaults instead of replacing
// the user's other preview choices with a hard-coded list.
#include <KIO/PreviewJob>
#include <QCoreApplication>
#include <QTextStream>
#include <KFileItem>
#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <sys/stat.h>

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    if (app.arguments().contains(QStringLiteral("--home-folders"))) {
        QJsonArray roots;
        const QDir home(QDir::homePath());
        for (const auto &entry : home.entryInfoList(QDir::Dirs | QDir::Hidden | QDir::NoDotAndDotDot | QDir::NoSymLinks)) {
            struct stat info;
            const auto path = entry.canonicalFilePath();
            if (::stat(QFile::encodeName(path).constData(), &info) != 0) continue;
            const QString identity = QString::number(quint64(info.st_dev)) + ':' + QString::number(quint64(info.st_ino));
            roots.append(QJsonObject{{"name", entry.fileName()}, {"id", identity},
                {"icon", KFileItem(QUrl::fromLocalFile(path)).iconName()}});
        }
        QTextStream(stdout) << QJsonDocument(QJsonObject{{"version", 1}, {"home", home.canonicalPath()},
            {"defaultHomeColor", "yellow"}, {"outsideHomeColor", "red"}, {"roots", roots}}).toJson();
        return 0;
    }
    QTextStream(stdout) << KIO::PreviewJob::defaultPlugins().join(',') << '\n';
    return 0;
}
