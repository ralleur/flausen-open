// SPDX-License-Identifier: MIT
#include "../quickpreview.h"
#include <QApplication>
#include <QAction>
#include <QClipboard>
#include <QDialog>
#include <QFile>
#include <QImage>
#include <QLineEdit>
#include <QMainWindow>
#include <QMediaPlayer>
#include <QPainter>
#include <QPdfDocument>
#include <QPdfView>
#include <QPdfWriter>
#include <QPlainTextEdit>
#include <QTemporaryDir>
#include <QTest>
#include <QVBoxLayout>

// Same QObject contract as Dolphin; selection remains unnotified until flushed.
class DolphinView : public QWidget {
    Q_OBJECT
public:
    using QWidget::QWidget;
    KFileItemList items;
Q_SIGNALS:
    void selectionChanged(const KFileItemList &items);
private Q_SLOTS:
    void emitSelectionChangedSignal() { Q_EMIT selectionChanged(items); }
};

class QuickPreviewTest : public QObject {
    Q_OBJECT
private:
    static QDialog *dialog(QMainWindow &window) { return window.findChild<QDialog *>("ralleurQuickPreviewDialog"); }
private Q_SLOTS:
    void opaqueBackgroundWithoutFocus() {
        QTemporaryDir temp;
        const auto path=temp.path()+"/wide.png";
        QImage image(100,10,QImage::Format_RGB32); image.fill(Qt::red); QVERIFY(image.save(path));
        QMainWindow window;
        auto view=new DolphinView(&window); window.setCentralWidget(view);
        view->setFocusPolicy(Qt::StrongFocus);
        view->items={KFileItem(QUrl::fromLocalFile(path))};
        Ralleur::QuickPreview controller(&window);
        window.show(); window.activateWindow(); view->setFocus();
        QTest::keyClick(view,Qt::Key_Space);
        auto preview=dialog(window); QVERIFY(preview);
        auto checkSurface=[preview] {
            const auto pixels=preview->grab().toImage();
            // The wide image leaves background above it. Only the rounded
            // exterior corners may be transparent, even after losing focus.
            QCOMPARE(pixels.pixelColor(pixels.width()/2,8).alpha(),255);
            QCOMPARE(pixels.pixelColor(0,0).alpha(),0);
        };
        checkSurface();
        window.activateWindow(); view->setFocus();
        QTRY_VERIFY(view->hasFocus());
        QVERIFY(!preview->isActiveWindow());
        checkSurface();
        QTest::keyClick(view,Qt::Key_Escape);
    }
    void toggleRepeatEscapeAndInput() {
        QTemporaryDir temp;
        const auto path=temp.path()+"/hello.txt";
        QFile file(path); QVERIFY(file.open(QIODevice::WriteOnly)); file.write("hello preview"); file.close();
        QMainWindow window;
        auto view=new DolphinView(&window);
        view->setFocusPolicy(Qt::StrongFocus);
        window.setCentralWidget(view);
        auto layout=new QVBoxLayout(view);
        auto editor=new QLineEdit(view); layout->addWidget(editor);
        auto rename=new QPlainTextEdit(view); layout->addWidget(rename);
        auto selection=new QAction(&window);
        selection->setObjectName("toggle_selection_mode");
        selection->setShortcut(Qt::Key_Space); window.addAction(selection);
        int selectionModeCalls=0;
        connect(selection,&QAction::triggered,&window,[&] { ++selectionModeCalls; });
        Ralleur::QuickPreview controller(&window);
        QVERIFY(!selection->shortcuts().contains(QKeySequence(Qt::Key_Space)));
        view->items={KFileItem(QUrl::fromLocalFile(path))};
        window.show(); window.activateWindow(); view->setFocus();
        qApp->clipboard()->setText("keep clipboard");
        QTest::keyClick(view,Qt::Key_Space);
        auto preview=dialog(window);
        QVERIFY(preview && preview->isVisible());
        QCOMPARE(preview->findChild<QPlainTextEdit *>()->toPlainText(),"hello preview");
        QCOMPARE(selectionModeCalls,0);
        QCOMPARE(qApp->clipboard()->text(),"keep clipboard");
        QKeyEvent repeat(QEvent::KeyPress,Qt::Key_Space,Qt::NoModifier," ",true,1);
        QApplication::sendEvent(preview,&repeat);
        QVERIFY(preview->isVisible());
        QPointer<QDialog> pointer=preview;
        QTest::keyClick(preview,Qt::Key_Space);
        QTRY_VERIFY(!pointer || !pointer->isVisible());
        QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
        view->setFocus();
        QTest::keyClick(view,Qt::Key_Space);
        preview=dialog(window); QVERIFY(preview && preview->isVisible());
        QTest::keyClick(preview,Qt::Key_Escape);
        QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
        editor->setFocus(); QTest::keyClick(editor,Qt::Key_Space); QCOMPARE(editor->text()," ");
        rename->setFocus(); QTest::keyClick(rename,Qt::Key_Space); QCOMPARE(rename->toPlainText()," ");
        QVERIFY(!dialog(window));
        QCOMPARE(selectionModeCalls,0);
        view->items.clear(); view->setFocus(); QTest::keyClick(view,Qt::Key_Space);
        QVERIFY(!dialog(window));
        QCOMPARE(selectionModeCalls,0);
    }
    void imagePdfAndIndependentSplitSelection() {
        QTemporaryDir temp;
        const auto imagePath=temp.path()+"/image.png",pdfPath=temp.path()+"/document.pdf";
        QImage image(100,60,QImage::Format_RGB32); image.fill(Qt::red); QVERIFY(image.save(imagePath));
        { QPdfWriter writer(pdfPath); QPainter painter(&writer); painter.drawText(100,100,"Preview PDF"); }
        QMainWindow window;
        auto container=new QWidget(&window);window.setCentralWidget(container);
        auto layout=new QVBoxLayout(container);
        auto first=new DolphinView(container),second=new DolphinView(container);
        first->setFocusPolicy(Qt::StrongFocus);second->setFocusPolicy(Qt::StrongFocus);
        layout->addWidget(first);layout->addWidget(second);
        first->items={KFileItem(QUrl::fromLocalFile(imagePath))};
        second->items={KFileItem(QUrl::fromLocalFile(pdfPath))};
        Ralleur::QuickPreview controller(&window);
        window.show();window.activateWindow();first->setFocus();
        QTest::keyClick(first,Qt::Key_Space);
        auto preview=dialog(window);QVERIFY(preview);
        QVERIFY(preview->findChild<QWidget *>("ralleurImagePreview"));
        QTest::keyClick(preview,Qt::Key_Space);
        QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
        second->setFocus();QTest::keyClick(second,Qt::Key_Space);
        preview=dialog(window);QVERIFY(preview);
        auto pdf=preview->findChild<QPdfView *>();QVERIFY(pdf);
        QCOMPARE(pdf->document()->pageCount(),1);
        QTest::keyClick(preview,Qt::Key_Escape);
    }
    void followsSelectionWithoutReopening() {
        QTemporaryDir temp;
        const auto textPath=temp.path()+"/hello.txt",imagePath=temp.path()+"/image.png",pdfPath=temp.path()+"/document.pdf";
        QFile file(textPath); QVERIFY(file.open(QIODevice::WriteOnly)); file.write("selected text"); file.close();
        QImage image(100,60,QImage::Format_RGB32); image.fill(Qt::red); QVERIFY(image.save(imagePath));
        { QPdfWriter writer(pdfPath); QPainter painter(&writer); painter.drawText(100,100,"Preview PDF"); }
        QMainWindow window;
        auto container=new QWidget(&window); window.setCentralWidget(container);
        auto layout=new QVBoxLayout(container);
        auto first=new DolphinView(container),second=new DolphinView(container);
        first->setFocusPolicy(Qt::StrongFocus); second->setFocusPolicy(Qt::StrongFocus);
        layout->addWidget(first); layout->addWidget(second);
        first->items={KFileItem(QUrl::fromLocalFile(textPath))};
        Ralleur::QuickPreview controller(&window);
        window.show(); window.activateWindow(); first->setFocus();
        QTest::keyClick(first,Qt::Key_Space);
        QPointer<QDialog> preview=dialog(window); QVERIFY(preview);
        const auto geometry=preview->geometry();
        // Clicking another file returns focus to Dolphin before its delayed signal.
        window.activateWindow(); first->setFocus();
        QTRY_VERIFY(first->hasFocus());
        first->items={KFileItem(QUrl::fromLocalFile(imagePath))};
        Q_EMIT first->selectionChanged(first->items);
        QCOMPARE(dialog(window),preview.data());
        QVERIFY(preview->isVisible());
        QCOMPARE(preview->geometry(),geometry);
        QVERIFY(preview->findChild<QWidget *>("ralleurImagePreview"));
        QVERIFY(!preview->findChild<QPlainTextEdit *>());
        QVERIFY(preview->windowTitle().contains("image.png"));
        // Unrelated split notifications cannot steal the preview.
        second->items={KFileItem(QUrl::fromLocalFile(pdfPath))};
        Q_EMIT second->selectionChanged(second->items);
        QVERIFY(!preview->findChild<QPdfView *>());
        second->setFocus(); Q_EMIT second->selectionChanged(second->items);
        auto pdf=preview->findChild<QPdfView *>(); QVERIFY(pdf);
        QPointer<QPdfDocument> document=pdf->document();
        QCOMPARE(document->pageCount(),1);
        // Repeated notifications preserve the loaded document and its scroll state.
        Q_EMIT second->selectionChanged(second->items);
        QCOMPARE(preview->findChild<QPdfView *>()->document(),document.data());
        second->items.clear(); Q_EMIT second->selectionChanged(second->items);
        QVERIFY(!document);
        QVERIFY(!preview->findChild<QPdfView *>());
        QVERIFY(preview->isVisible());
        second->items={KFileItem(QUrl::fromLocalFile(textPath))};
        Q_EMIT second->selectionChanged(second->items);
        QCOMPARE(preview->findChild<QPlainTextEdit *>()->toPlainText(),"selected text");
        QCOMPARE(preview->geometry(),geometry);
        const auto audioPath=temp.path()+"/silent.wav";
        QFile audio(audioPath); QVERIFY(audio.open(QIODevice::WriteOnly));
        audio.write(QByteArray::fromHex("524946462400000057415645666d74201000000001000100401f0000803e0000020010006461746100000000"));
        audio.close();
        second->items={KFileItem(QUrl::fromLocalFile(audioPath))};
        Q_EMIT second->selectionChanged(second->items);
        QPointer<QMediaPlayer> player=preview->findChild<QMediaPlayer *>(); QVERIFY(player);
        second->items={KFileItem(QUrl::fromLocalFile(textPath))};
        Q_EMIT second->selectionChanged(second->items);
        QVERIFY(!player);
        QTest::keyClick(second,Qt::Key_Escape);
        QTRY_VERIFY(!preview || !preview->isVisible());
    }
};
int main(int argc,char **argv) {
    QApplication app(argc,argv);
    QuickPreviewTest test;
    return QTest::qExec(&test,argc,argv);
}
#include "quickpreview_test.moc"
