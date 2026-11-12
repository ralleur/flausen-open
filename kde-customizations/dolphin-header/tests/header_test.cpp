// SPDX-License-Identifier: MIT
#include "../header.h"
#include <QDialog>
#include <QApplication>
#include <QDockWidget>
#include <QMainWindow>
#include <QTemporaryDir>
#include <QTest>
#include <QToolBar>
#include <QToolButton>
#include <QWidgetAction>
#include <QGraphicsView>
#include <QGraphicsScene>
#include <QTabWidget>
#include <QTabBar>
#include <QVBoxLayout>
#include <KUrlNavigator>
#include <KFilePlacesView>
#include <KFilePlacesModel>

class DolphinView : public QWidget {
    Q_OBJECT
public:
    using QWidget::QWidget;
};

class DolphinMainWindow : public QMainWindow {
    Q_OBJECT
public:
    bool rejectClose = false;
    DolphinMainWindow() {
        setObjectName("Dolphin_Test");
        auto toolbar = addToolBar("Main");
        toolbar->setObjectName("mainToolBar");
        toolbar->addAction("Search");
        resize(900, 460);
    }
protected:
    void closeEvent(QCloseEvent *event) override {
        if (rejectClose) event->ignore();
        else QMainWindow::closeEvent(event);
    }
};

class HeaderTest : public QObject {
    Q_OBJECT
private Q_SLOTS:
    void onlyDolphinMainWindows() {
        QMainWindow other;
        other.addToolBar("Main")->setObjectName("mainToolBar");
        const auto flags = other.windowFlags();
        QVERIFY(!Ralleur::Integration::attach(&other));
        QCOMPARE(other.windowFlags(), flags);
        DolphinMainWindow incomplete;
        incomplete.findChild<QToolBar *>()->setObjectName("otherToolbar");
        QVERIFY(!Ralleur::Integration::attach(&incomplete));
    }
    void controlsAndNativeStates() {
        DolphinMainWindow window;
        window.show();
        auto header = Ralleur::Integration::attach(&window);
        QVERIFY(header);
        QVERIFY(!header->decorated());
        QCOMPARE(Ralleur::Integration::attach(&window), header);
        QCOMPARE(window.findChildren<QToolButton *>("ralleurClose").size(), 1);
        header->maximizeRestore();
        QVERIFY(window.isMaximized());
        header->maximizeRestore();
        QVERIFY(!window.isMaximized());
        header->minimize();
        QVERIFY(window.isMinimized());
        window.showNormal();
        window.rejectClose = true;
        header->closeWindow();
        QVERIFY(window.isVisible()); // Multi-tab and operation confirmations must be honored.
        window.rejectClose = false;
        header->closeWindow();
        QVERIFY(!window.isVisible());
    }
    void separateWindowsAndDialogs() {
        DolphinMainWindow first, second;
        second.setObjectName("Dolphin_Test2");
        first.show(); second.show();
        auto a = Ralleur::Integration::attach(&first);
        auto b = Ralleur::Integration::attach(&second);
        a->maximizeRestore();
        QVERIFY(first.isMaximized());
        QVERIFY(!second.isMaximized());
        QDialog dialog(&first);
        const auto flags = dialog.windowFlags();
        dialog.show();
        QCoreApplication::processEvents();
        QCOMPARE(dialog.windowFlags(), flags);
        QVERIFY(!dialog.findChild<QToolButton *>("ralleurClose"));
        b->closeWindow();
        QVERIFY(first.isVisible());
    }
    void toolbarReconfiguration() {
        DolphinMainWindow window;
        auto header = Ralleur::Integration::attach(&window);
        auto toolbar = window.findChild<QToolBar *>();
        auto controls = toolbar->actions().last();
        QCOMPARE(controls->objectName(), "ralleurWindowControlsAction");
        toolbar->removeAction(controls);
        QCoreApplication::processEvents();
        QTRY_VERIFY(toolbar->actions().contains(controls));
        toolbar->addAction("New tool");
        QTRY_COMPARE(toolbar->actions().last(), controls);
        QCOMPARE(window.findChildren<QToolButton *>("ralleurClose").size(), 1);
        QVERIFY(header);
    }
    void nativePlacesMouseHandling() {
        DolphinMainWindow window;
        auto dock = new QDockWidget("Places", &window);
        auto places = new KFilePlacesView(dock);
        auto model = new KFilePlacesModel(places);
        places->setModel(model);
        dock->setWidget(places);
        window.addDockWidget(Qt::LeftDockWidgetArea, dock);
        auto nativeDelegate = places->itemDelegate();
        window.show();
        QVERIFY(Ralleur::Integration::attach(&window));
        QCOMPARE(places->itemDelegate(), nativeDelegate);
        QCoreApplication::processEvents();
        if (model->rowCount() > 0) {
            auto first = model->index(0, 0);
            const auto position = places->visualRect(first).center();
            QTest::mouseMove(places->viewport(), position);
            QTest::mouseClick(places->viewport(), Qt::LeftButton, {}, position);
            QCOMPARE(places->currentIndex(), first);
        }
    }
    void followsLiveThemeIncludingForegroundAndChrome() {
        const auto original=qApp->palette();
        DolphinMainWindow window;
        auto tabs=new QTabWidget(&window);
        auto view=new DolphinView(tabs);
        auto graphics=new QGraphicsView(view);
        auto scene=new QGraphicsScene(graphics);graphics->setScene(scene);
        auto layout=new QVBoxLayout(view);layout->addWidget(graphics);
        tabs->addTab(view,"Files");window.setCentralWidget(tabs);
        auto places=new KFilePlacesModel(&window);
        auto navigator=new KUrlNavigator(places,QUrl::fromLocalFile("/tmp"),&window);
        window.findChild<QToolBar *>()->addWidget(navigator);
        const auto globalStyle=qApp->styleSheet();
        window.show();QVERIFY(Ralleur::Integration::attach(&window));
        QCOMPARE(qApp->styleSheet(),globalStyle);
        for (const auto &background : {QColor("#101316"),QColor("#172a3c"),QColor("#f5f2ee"),QColor("#101316")}) {
            auto theme=original;
            const bool dark=background.lightness()<128;
            theme.setColor(QPalette::Window,background);
            theme.setColor(QPalette::Base,background);
            theme.setColor(QPalette::WindowText,dark?QColor("#eef3fc"):QColor("#182430"));
            theme.setColor(QPalette::Text,theme.color(QPalette::WindowText));
            theme.setColor(QPalette::Highlight,dark?QColor("#ca7562"):QColor("#365eb8"));
            theme.setColor(QPalette::AlternateBase,dark?QColor("#283344"):QColor("#e9e5df"));
            qApp->setPalette(theme);
            const auto base=dark?QColor(background.red()+10,background.green()+10,background.blue()+10):background;
            QTRY_COMPARE(graphics->palette().color(QPalette::Base),base);
            QTRY_COMPARE(scene->palette().color(QPalette::Text),theme.color(QPalette::Text));
            QCOMPARE(scene->palette().color(QPalette::Highlight),theme.color(QPalette::Highlight));
            QCOMPARE(scene->palette().color(QPalette::AlternateBase),theme.color(QPalette::AlternateBase));
            QCOMPARE(navigator->palette().color(QPalette::Window),background);
            QCOMPARE(tabs->tabBar()->palette().color(QPalette::Window),background);
            QCOMPARE(tabs->tabBar()->palette().color(QPalette::WindowText),theme.color(QPalette::WindowText));
            QCOMPARE(window.findChild<QToolButton *>("ralleurClose")->palette().color(QPalette::ButtonText),theme.color(QPalette::ButtonText));
        }
        qApp->setPalette(original);
    }
    void transparentCornersAfterLateAttachAndResize() {
        DolphinMainWindow window;
        window.show(); // Exercise the late-attachment fallback as well.
        auto header = Ralleur::Integration::attach(&window);
        QVERIFY(header);
        QCOMPARE(header->alphaBufferSize(), 8);
        auto checkCorners = [&window] {
            const auto image = window.grab().toImage();
            for (const auto point : {QPoint(0, 0), QPoint(image.width()-1, 0),
                                    QPoint(0, image.height()-1), QPoint(image.width()-1, image.height()-1)})
                QVERIFY2(image.pixelColor(point).alpha() == 0, "Rounded window corner must have zero alpha.");
            QVERIFY(image.pixelColor(image.width()/2, image.height()/2).alpha() > 0);
        };
        checkCorners();
        window.resize(740, 400);
        QCoreApplication::processEvents();
        checkCorners();
        header->maximizeRestore();
        header->maximizeRestore();
        QCoreApplication::processEvents();
        checkCorners();
    }
};
int main(int argc, char **argv) {
    QTemporaryDir isolated;
    qputenv("XDG_CONFIG_HOME", (isolated.path()+"/config").toLocal8Bit());
    qputenv("XDG_DATA_HOME", (isolated.path()+"/data").toLocal8Bit());
    QApplication app(argc, argv);
    HeaderTest test;
    return QTest::qExec(&test, argc, argv);
}
#include "header_test.moc"
