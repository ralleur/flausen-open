#include "../../dialogs/dialogstyle.h"
#include <QApplication>
#include <QSlider>
#include <QStyleFactory>
#include <QStyleOptionSlider>
#include <QTest>
#include <QPainter>
class SliderTest : public QObject {
    Q_OBJECT
private slots:
    void followsPaletteHighlight() {
        qApp->setStyle(new RalleurDialogStyle(QStyleFactory::create("Fusion")));
        QSlider slider(Qt::Horizontal);
        slider.resize(420, 40);
        slider.setValue(50);
        slider.show();
        for (const QColor &accent : {QColor("#e83279"), QColor("#32b578")}) {
            auto palette = slider.palette();
            palette.setColor(QPalette::Highlight, accent);
            slider.setPalette(palette);
            const auto image = slider.grab().toImage();
            int matchingPixels = 0;
            for (int y = 0; y < image.height(); ++y)
                for (int x = 0; x < image.width(); ++x)
                    if (image.pixelColor(x, y) == accent) ++matchingPixels;
            QVERIFY(matchingPixels > 100);
        }
    }
    void nativeGeometryAndInput() {
        qApp->setStyle(new RalleurDialogStyle(QStyleFactory::create("Fusion")));
        for (auto orientation : {Qt::Horizontal, Qt::Vertical}) {
            for (bool inverted : {false, true}) {
                QSlider slider(orientation);
                slider.setRange(-20, 80); slider.setValue(30);
                slider.setInvertedAppearance(inverted);
                slider.resize(orientation == Qt::Horizontal ? QSize(420,40) : QSize(40,240));
                slider.show(); slider.setFocus();
                QTest::keyClick(&slider, Qt::Key_Right);
                QCOMPARE(slider.value(), 31);
                for (int value : {-20, 30, 80}) {
                    slider.setValue(value);
                    auto pixmap = slider.grab();
                    QVERIFY(!pixmap.isNull());
                    if (orientation == Qt::Horizontal && !inverted && value == 30)
                        pixmap.save("native-slider.png");
                }
                slider.setEnabled(false);
                QTest::mouseClick(&slider, Qt::LeftButton, {}, QPoint(10,10));
                QCOMPARE(slider.value(), 80);
            }
        }
    }
};
QTEST_MAIN(SliderTest)
#include "native_test.moc"
