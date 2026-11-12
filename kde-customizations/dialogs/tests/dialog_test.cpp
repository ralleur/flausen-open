// SPDX-License-Identifier: MIT
#include "../dialogstyle.h"
#include <QApplication>
#include <QDialog>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QMessageBox>
#include <QMenu>
#include <QFileDialog>
#include <QCheckBox>
#include <QSignalSpy>
#include <QTest>
#include <QStyleFactory>
#include <QVBoxLayout>
class DialogTest : public QObject {
    Q_OBJECT
private slots:
    void initTestCase() { qApp->setStyle(new RalleurDialogStyle(QStyleFactory::create("Fusion"))); }
    void rolesAndKeyboard() {
        QPalette palette = qApp->palette(); palette.setColor(QPalette::Window, QColor("#151719")); qApp->setPalette(palette);
        QMessageBox box(QMessageBox::Warning, "Trash", "Move to Trash?", QMessageBox::NoButton);
        auto trash = box.addButton("Papierkorb", QMessageBox::DestructiveRole);
        auto cancel = box.addButton(QMessageBox::Cancel);
        box.setDefaultButton(cancel);
        box.show();
        QTRY_COMPARE(trash->property("ralleurAction").toString(), QString("destructive"));
        QVERIFY(box.styleSheet().contains("#1c1f21"));
        QSignalSpy finished(&box, &QDialog::finished);
        QTest::keyClick(&box, Qt::Key_Escape);
        QTRY_COMPARE(finished.count(), 1);
        QCOMPARE(box.clickedButton(), cancel);
        box.show(); QTest::mouseClick(trash, Qt::LeftButton); QCOMPARE(box.clickedButton(), trash);
    }
    void lightAndPaletteSwitch() {
        QPalette palette = qApp->palette(); palette.setColor(QPalette::Window, QColor("#ffffff")); qApp->setPalette(palette);
        QMessageBox box(QMessageBox::Question, "Confirm", "Continue?", QMessageBox::Ok | QMessageBox::Cancel);
        box.show();
        QTRY_VERIFY(box.styleSheet().contains("#f8f6f3"));
        QCOMPARE(box.button(QMessageBox::Ok)->property("ralleurAction").toString(), QString("primary"));
        palette.setColor(QPalette::Window, QColor("#151719")); qApp->setPalette(palette);
        QTRY_VERIFY(box.styleSheet().contains("#1c1f21"));
    }
    void fileDialogAndAppScope() {
        QWidget window; QPushButton ordinary("Normal", &window); window.show();
        QFileDialog file; file.setOption(QFileDialog::DontUseNativeDialog); file.show();
        QTRY_VERIFY(!file.styleSheet().isEmpty());
        QVERIFY(ordinary.styleSheet().isEmpty()); QVERIFY(window.styleSheet().isEmpty());
        QCOMPARE(window.windowFlags() & Qt::FramelessWindowHint, Qt::WindowFlags());
    }
    void customStylePreserved() {
        QDialog dialog; dialog.setStyleSheet("QDialog { background: magenta; }"); dialog.show();
        QTest::qWait(10); QCOMPARE(dialog.styleSheet(), QString("QDialog { background: magenta; }"));
    }
    void menuNavigation() {
        QMenu menu;
        auto disabled = menu.addAction("Einfügen"); disabled->setEnabled(false);
        auto sub = menu.addMenu("Sortieren nach");
        auto selected = sub->addAction("Name"); selected->setCheckable(true); selected->setChecked(true);
        auto action = menu.addAction("Eigenschaften");
        QSignalSpy triggered(action, &QAction::triggered);
        menu.popup(QPoint(20,20));
        QTRY_VERIFY(menu.styleSheet().contains("border-radius: 14px"));
        menu.setActiveAction(action); QTest::keyClick(&menu, Qt::Key_Return);
        QTRY_COMPARE(triggered.count(), 1);
        QVERIFY(!disabled->isEnabled()); QVERIFY(selected->isChecked());
        sub->popup(QPoint(20,20)); QTRY_VERIFY(!sub->styleSheet().isEmpty());
        QTest::keyClick(sub, Qt::Key_Escape); QTRY_VERIFY(!sub->isVisible());
    }
    void glassMenuPreserved() {
        QMenu menu;
        menu.addAction("zippen");
        menu.ensurePolished();
        menu.setProperty("ralleurGlassMenu", true);
        menu.setProperty("ralleurDialogUpdating", true);
        const QString css = "QMenu { background: rgba(28,32,36,64); }";
        menu.setStyleSheet(css);
        menu.setProperty("ralleurDialogUpdating", false);
        menu.popup(QPoint(20,20));
        QCoreApplication::processEvents();
        QCOMPARE(menu.styleSheet(), css);
        QEvent palette(QEvent::ApplicationPaletteChange);
        QApplication::sendEvent(&menu, &palette);
        QCOMPARE(menu.styleSheet(), css);
        menu.close();
    }
    void styleReplacement() {
        QDialog dialog; dialog.show(); QTRY_VERIFY(!dialog.styleSheet().isEmpty());
        qApp->setStyle(QStyleFactory::create("Fusion"));
        QCoreApplication::processEvents();
        QVERIFY(dialog.styleSheet().isEmpty());
    }
};
QTEST_MAIN(DialogTest)
#include "dialog_test.moc"
