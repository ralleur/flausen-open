// SPDX-License-Identifier: MIT
#include "../foldercolors.h"
#include <KConfig>
#include <KConfigGroup>
#include <KFileItem>
#include <QApplication>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QTemporaryDir>
#include <QTest>

class FolderColorsTest : public QObject {
    Q_OBJECT
private:
    static void write(const QString &path, const QByteArray &bytes) {
        QFile file(path); QVERIFY(file.open(QIODevice::WriteOnly)); QCOMPARE(file.write(bytes), bytes.size());
    }
    static QString icon(const QString &path) { return KFileItem(QUrl::fromLocalFile(path)).iconName(); }
    static Ralleur::FolderPolicy policy(const QString &home, const QString &old) {
        Ralleur::FolderPolicy result;
        result.data = {{"version", 1}, {"home", home}, {"defaultHomeColor", "yellow"}, {"outsideHomeColor", "red"},
                      {"roots", QJsonArray{QJsonObject{{"id", Ralleur::directoryIdentity(old)}, {"icon", "folder-pictures"}}}}};
        return result;
    }
private Q_SLOTS:
    void categoriesNewFoldersRenameAndSymlinks() {
        QTemporaryDir temp;
        const auto home = temp.path()+"/home", old = home+"/Pictures", outside = temp.path()+"/external";
        QDir().mkpath(old+"/nested"); QDir().mkpath(home+"/new/child"); QDir().mkpath(outside);
        auto p = policy(home, old);
        QCOMPARE(p.colorForPath(old+"/nested"), "violet");
        QCOMPARE(p.colorForPath(home+"/new/child"), "yellow");
        QCOMPARE(p.colorForPath(outside), "red");
        QVERIFY(QFile::link(outside, home+"/external-link"));
        QCOMPARE(p.colorForPath(home+"/external-link"), "red");
        QVERIFY(QDir().rename(old, home+"/Renamed"));
        QCOMPARE(p.colorForPath(home+"/Renamed/nested"), "violet");
        QVERIFY(QDir().mkpath(old));
        QCOMPARE(p.colorForPath(old), "yellow");
        write(home+"/Renamed/.directory", "[Desktop Entry]\nIcon=folder-green\n");
        QCOMPARE(p.colorForPath(home+"/Renamed/nested"), "green");
    }
    void nativeMetadataAndJournalPreserveUserFields() {
        QTemporaryDir temp;
        const auto home=temp.path()+"/home", old=home+"/Pictures", journal=temp.path()+"/journal";
        QDir().mkpath(old+"/Child"); QDir().mkpath(home+"/Fresh");
        auto p=policy(home, old);
        write(old+"/Child/.directory", "[Desktop Entry]\nIcon=folder-blue\nComment=Keep this\n[Other]\nValue=42\n");
        QCOMPARE(Ralleur::applyFolderColors(p, old, journal).size(), 1);
        QCOMPARE(icon(old+"/Child"), "folder-violet");
        KConfig config(old+"/Child/.directory", KConfig::SimpleConfig);
        QCOMPARE(KConfigGroup(&config,"Desktop Entry").readEntry("Comment",QString()), "Keep this");
        QCOMPARE(KConfigGroup(&config,"Other").readEntry("Value",0), 42);
        QCOMPARE(Ralleur::applyFolderColors(p, old, journal).size(), 0);
        QCOMPARE(Ralleur::applyFolderColors(p, home, journal).size(), 2);
        QCOMPARE(icon(home+"/Fresh"), "folder-yellow");
        const auto files=QDir(journal).entryList({"*.json"},QDir::Files);
        QCOMPARE(files.size(), 3);
        write(old+"/Child/.directory", "[Desktop Entry]\nIcon=folder-cyan\nComment=Manual edit\n");
        QCOMPARE(Ralleur::applyFolderColors(p, old, journal).size(), 0);
        QCOMPARE(icon(old+"/Child"), "folder-cyan");
    }
    void outsideDefaultDoesNotClutterAndSpecialIconsSurvive() {
        QTemporaryDir temp;
        const auto home=temp.path()+"/home", outside=temp.path()+"/outside";
        QDir().mkpath(home+"/Old"); QDir().mkpath(outside+"/Ordinary"); QDir().mkpath(outside+"/Colored");
        QDir().mkpath(outside+"/.git/internal"); QDir().mkpath(outside+"/App");
        auto p=policy(home, home+"/Old");
        write(outside+"/Colored/.directory", "[Desktop Entry]\nIcon=folder-green\n");
        write(outside+"/App/.directory", "[Desktop Entry]\nIcon=application-x-executable\n");
        QCOMPARE(Ralleur::applyFolderColors(p,outside,temp.path()+"/journal").size(),1);
        QVERIFY(!QFile::exists(outside+"/Ordinary/.directory"));
        QVERIFY(!QFile::exists(outside+"/.git/.directory"));
        QCOMPARE(icon(outside+"/Colored"),"folder-red");
        QCOMPARE(icon(outside+"/App"),"application-x-executable");
    }
    void watcherColorsNewChildren() {
        QTemporaryDir temp;
        const auto home=temp.path()+"/home", old=home+"/Pictures";
        QDir().mkpath(old);
        auto p=policy(home,old);
        Ralleur::FolderColors controller(p,temp.path()+"/journal");
        QObject source;
        controller.watchPath(&source,old);
        QTest::qWait(180);
        QVERIFY(QDir().mkpath(old+"/Created later"));
        QTRY_COMPARE_WITH_TIMEOUT(icon(old+"/Created later"),"folder-violet",4000);
        QVERIFY(QDir().mkpath(home+"/New home folder"));
        QTRY_COMPARE_WITH_TIMEOUT(icon(home+"/New home folder"),"folder-yellow",4000);
    }
};
int main(int argc,char **argv) {
    QTemporaryDir isolated;
    qputenv("XDG_CONFIG_HOME",(isolated.path()+"/config").toUtf8());
    qputenv("XDG_DATA_HOME",(isolated.path()+"/data").toUtf8());
    QApplication app(argc,argv);
    FolderColorsTest test;
    return QTest::qExec(&test,argc,argv);
}
#include "foldercolors_test.moc"
