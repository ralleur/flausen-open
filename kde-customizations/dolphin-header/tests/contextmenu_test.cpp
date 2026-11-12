// SPDX-License-Identifier: MIT
#include "../contextmenu.h"
#include <QApplication>
#include <QFile>
#include <QMenu>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QtTest>
#include <KLocalizedString>
#include <KFileItemActions>
#include <KFileItemListProperties>

class DolphinContextMenu : public QMenu { Q_OBJECT };
class ContextMenuTest : public QObject {
    Q_OBJECT
private Q_SLOTS:
    void initTestCase() {
        KLocalizedString::setApplicationDomain("dolphin");
        KLocalizedString::setLanguages({qEnvironmentVariable("RALLEUR_TEST_LANGUAGE", "en_US")});
    }
    void shiftAndForwarding() {
        Ralleur::ContextMenus filter;
        DolphinContextMenu menu;
        auto options = new QMenu(&menu);
        options->addAction("tar.gz");
        auto zip = options->addAction("zip");
        options->addAction("custom");
        auto native = menu.addAction(QIcon::fromTheme("archive-insert"), "Komprimieren");
        native->setMenu(options);
        auto duplicate = menu.addAction("Hier duplizieren");
        duplicate->setObjectName("duplicate");
        QSignalSpy executed(zip, &QAction::triggered);
        menu.popup(QPoint(20,20));
        QVERIFY(menu.property("ralleurGlassMenu").toBool());
        QVERIFY(menu.styleSheet().contains("rgba("));
        QVERIFY(menu.testAttribute(Qt::WA_TranslucentBackground));
        QVERIFY(!menu.actions().contains(duplicate));
        QVERIFY(duplicate->isEnabled());
        auto action = menu.actions().first();
        QCOMPARE(action->text(), "zippen");
        QVERIFY(!action->menu());
        action->trigger();
        QCOMPARE(executed.count(), 1);
        QTest::keyPress(&menu, Qt::Key_Shift);
        QCOMPARE(action->menu(), options);
        QTest::keyRelease(&menu, Qt::Key_Shift);
        QVERIFY(!action->menu());
        zip->setEnabled(false);
        QVERIFY(!action->isEnabled());
        Ralleur::ContextMenus::setShift(&menu, true);
        QVERIFY(action->isEnabled());
        QCOMPARE(action->menu(), options);
        Ralleur::ContextMenus::prepare(&menu, false);
        QCOMPARE(menu.actions().size(), 1);
        QVERIFY(!action->menu());
    }
    void nativePlugins() {
        QTemporaryDir dir;
        QVERIFY(dir.isValid());
        QFile file(dir.filePath("sample.txt"));
        QVERIFY(file.open(QIODevice::WriteOnly));
        file.write("ZIP integration test\n"); file.close();
        QWidget window;
        KFileItemActions actions;
        actions.setParentWidget(&window);
        actions.setItemListProperties(KFileItemListProperties(KFileItemList{KFileItem(QUrl::fromLocalFile(file.fileName()))}));
        QMenu menu;
        actions.addActionsTo(&menu, KFileItemActions::MenuActionSource::Plugins);
        for (auto action : menu.actions())
            qInfo() << "Native:" << action->text() << action->icon().name();
        Ralleur::ContextMenus::prepare(&menu, false);
        QAction *zip = nullptr;
        for (auto action : menu.actions()) {
            QVERIFY(action->icon().name() != "tag");
            QVERIFY(action->icon().name() != "activities");
            QVERIFY(!action->text().contains("neuen Ordner"));
            QVERIFY(!action->text().contains("New Folder"));
            if (action->objectName() == "ralleurZip") zip = action;
        }
        QVERIFY(zip);
        QVERIFY(!zip->menu());
        QTRY_VERIFY_WITH_TIMEOUT(zip->isEnabled(), 5000);
        if (!qEnvironmentVariableIsSet("RALLEUR_TEST_ARCHIVE")) return;
        zip->trigger();
        QTRY_VERIFY_WITH_TIMEOUT(QFile::exists(dir.filePath("sample.zip")), 15000);
        QFile archive(dir.filePath("sample.zip"));
        QVERIFY(archive.open(QIODevice::ReadOnly));
        QCOMPARE(archive.read(2), QByteArray("PK"));
    }
};
QTEST_MAIN(ContextMenuTest)
#include "contextmenu_test.moc"
