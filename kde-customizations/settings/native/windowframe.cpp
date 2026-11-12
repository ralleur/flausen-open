// SPDX-License-Identifier: MIT
#include "windowframe.h"
#include <QQuickWindow>
#include <QEvent>
#include <QPainterPath>
#include <QRegion>
#include <QTimer>
#include <KWindowShadow>
#include <cmath>
namespace {
constexpr int Radius = 12;
KWindowShadowTile::Ptr tile(const QImage &image, const QRect &rect) {
    auto result = KWindowShadowTile::Ptr::create();
    result->setImage(image.copy(rect));
    return result;
}
}
WindowFrame::WindowFrame(QQuickItem *parent) : QQuickItem(parent) {
    connect(this, &QQuickItem::windowChanged, this, &WindowFrame::attach);
}
bool WindowFrame::shadowCreated() const { return m_shadow && m_shadow->isCreated(); }
void WindowFrame::attach(QQuickWindow *window) {
    if (m_window) m_window->removeEventFilter(this);
    delete m_shadow;
    m_shadow = nullptr;
    m_window = window;
    if (!window) return;
    window->installEventFilter(this);
    constexpr int pad = 24, corner = pad + Radius, extent = corner * 2 + 1;
    QImage image(extent, extent, QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    for (int y = 0; y < extent; ++y) {
        for (int x = 0; x < extent; ++x) {
            const double dx = std::abs(x - extent / 2.0) - .5;
            const double dy = std::abs(y - extent / 2.0 - 2) - .5;
            const double distance = qMax(0.0, std::hypot(qMax(0.0, dx), qMax(0.0, dy)) - Radius);
            image.setPixelColor(x, y, QColor(0, 0, 0, qRound(70 * std::exp(-distance * distance / 110.0))));
        }
    }
    m_shadow = new KWindowShadow(this);
    m_shadow->setTopLeftTile(tile(image, {0, 0, corner, corner}));
    m_shadow->setTopTile(tile(image, {corner, 0, 1, corner}));
    m_shadow->setTopRightTile(tile(image, {corner + 1, 0, corner, corner}));
    m_shadow->setRightTile(tile(image, {corner + 1, corner, corner, 1}));
    m_shadow->setBottomRightTile(tile(image, {corner + 1, corner + 1, corner, corner}));
    m_shadow->setBottomTile(tile(image, {corner, corner + 1, 1, corner}));
    m_shadow->setBottomLeftTile(tile(image, {0, corner + 1, corner, corner}));
    m_shadow->setLeftTile(tile(image, {0, corner, corner, 1}));
    m_shadow->setPadding(QMargins(pad, pad, pad, pad));
    m_shadow->setWindow(m_window);

    QTimer::singleShot(0, this, &WindowFrame::updateFrame);
}
void WindowFrame::updateFrame() {
    if (!m_window) return;
    const bool square = m_window->windowState() & (Qt::WindowMaximized | Qt::WindowFullScreen);
    if (square) m_window->setMask({});
    else {
        QPainterPath shape;
        shape.addRoundedRect(QRectF(0, 0, m_window->width(), m_window->height()), Radius, Radius);
        m_window->setMask(QRegion(shape.toFillPolygon().toPolygon()));
    }
    if (m_shadow) {
        if (square || !m_window->isVisible()) m_shadow->destroy();
        else if (!m_shadow->isCreated()) m_shadow->create();
    }
    emit changed();
}
bool WindowFrame::eventFilter(QObject *object, QEvent *event) {
    if (event->type() == QEvent::Resize || event->type() == QEvent::WindowStateChange
        || event->type() == QEvent::Expose || event->type() == QEvent::Show || event->type() == QEvent::Hide)
        QTimer::singleShot(0, this, &WindowFrame::updateFrame);
    return QQuickItem::eventFilter(object, event);
}
