#pragma once
#include <QPainter>
#include <QPainterPath>
#include <QColor>

namespace RalleurControls {
enum class Symbol { Minimize, Maximize, Close };
constexpr int ButtonSize = 30;
constexpr int IconSize = 16;
constexpr int Gap = 6;

// Shared by the compositor decoration and Dolphin/portal toolbar controls.
inline void paint(QPainter &p, const QRectF &rect, Symbol symbol,
                  QColor foreground, bool active, bool hovered, bool pressed)
{
    p.save();
    p.setRenderHint(QPainter::Antialiasing);
    if (!active) foreground.setAlphaF(foreground.alphaF() * .55);
    if (hovered || pressed) {
        QColor background = foreground;
        background.setAlphaF(pressed ? .20 : .12);
        p.setPen(Qt::NoPen);
        p.setBrush(background);
        const QPointF center = rect.center();
        p.drawRoundedRect(QRectF(center.x()-14, center.y()-14, 28, 28), 4, 4);
    }
    p.translate(rect.center() - QPointF(8, 8));
    QPen pen(foreground, 1.2, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin);
    p.setPen(pen);
    p.setBrush(Qt::NoBrush);
    switch (symbol) {
    case Symbol::Minimize: p.drawLine(QPointF(4,11.5), QPointF(12,11.5)); break;
    case Symbol::Maximize: p.drawRect(QRectF(4.5,4.5,7,7)); break;
    case Symbol::Close:
        p.drawLine(QPointF(4.5,4.5), QPointF(11.5,11.5));
        p.drawLine(QPointF(11.5,4.5), QPointF(4.5,11.5)); break;
    }
    p.restore();
}
}
