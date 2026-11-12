// SPDX-License-Identifier: MIT
#include "dialogstyle.h"
#include <QApplication>
#include <QDialog>
#include <QDialogButtonBox>
#include <QEvent>
#include <QLabel>
#include <QPushButton>
#include <QTimer>
#include <QPointer>
#include <QMessageBox>
#include <QLayout>
#include <QScreen>
#include <QMenu>
#include <QStyleOptionSlider>
#include <QSlider>
#include <QPainter>
#include <algorithm>
#include <cmath>

RalleurDialogStyle::RalleurDialogStyle(QStyle *base) : QProxyStyle(base) {}

void RalleurDialogStyle::drawComplexControl(ComplexControl control, const QStyleOptionComplex *option, QPainter *painter, const QWidget *widget) const
{
    const auto *slider = qstyleoption_cast<const QStyleOptionSlider *>(option);
    if (control != CC_Slider || !slider) {
        QProxyStyle::drawComplexControl(control, option, painter, widget);
        return;
    }
    // Keep base-style geometry and hit tests, including inverted/RTL sliders.
    const QRect handle = subControlRect(CC_Slider, slider, SC_SliderHandle, widget);
    const bool vertical = slider->orientation == Qt::Vertical;
    const bool light = slider->palette.color(QPalette::Window).lightness() > 140;
    const QRect rect = slider->rect;
    const qreal extent = vertical ? rect.height() : rect.width();
    const qreal inset = (vertical ? handle.height() : handle.width()) / 2.0;
    const qreal length = std::max(1.0, extent - 2 * inset);
    const int count = std::clamp(int(length / 10) + 1, 2, 60);
    const qreal pitch = length / (count - 1);
    const qreal thin = std::max(2.0, std::min(8.0, pitch - 3));
    const qreal thick = std::max(2.0, std::min(24.0, (vertical ? rect.width() : rect.height()) - 6.0));
    const double position = slider->maximum == slider->minimum ? 0.0 :
        double(qint64(slider->sliderPosition) - slider->minimum) / (qint64(slider->maximum) - slider->minimum);
    const int current = qRound(position * (count - 1));
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    if (!(slider->state & State_Enabled)) painter->setOpacity(0.4);
    for (int i = 0; i < count; ++i) {
        const int visual = slider->upsideDown ? count - 1 - i : i;
        const qreal center = inset + visual * pitch;
        const QRectF segment = vertical
            ? QRectF(rect.center().x() - thick / 2, rect.top() + center - thin / 2, thick, thin)
            : QRectF(rect.left() + center - thin / 2, rect.center().y() - thick / 2, thin, thick);
        painter->setPen(Qt::NoPen);
        painter->setBrush(position > 0 && i <= current ? slider->palette.color(QPalette::Highlight) : QColor(light ? "#c2c5c9" : "#575b60"));
        painter->drawRoundedRect(segment, 1.8, 1.8);
        if (i == current) {
            painter->setBrush(Qt::NoBrush);
            painter->setPen(QPen(QColor(light ? "#333b45" : "#e2e5e8"), slider->state & State_HasFocus ? 2.0 : 1.3));
            painter->drawRoundedRect(segment.adjusted(-2, -2, 2, 2), 3, 3);
        }
    }
    if (slider->tickPosition != QSlider::NoTicks) {
        QStyleOptionSlider ticks(*slider);
        ticks.subControls = SC_SliderTickmarks;
        QProxyStyle::drawComplexControl(control, &ticks, painter, widget);
    }
    painter->restore();
}

int RalleurDialogStyle::styleHint(StyleHint hint, const QStyleOption *option, const QWidget *widget, QStyleHintReturn *data) const
{
    if (hint == SH_DialogButtonBox_ButtonsHaveIcons && widget && qobject_cast<const QDialog *>(widget->window())) return 0;
    return QProxyStyle::styleHint(hint, option, widget, data);
}

void RalleurDialogStyle::polish(QWidget *widget)
{
    QProxyStyle::polish(widget);
    if ((!qobject_cast<QDialog *>(widget) && !qobject_cast<QMenu *>(widget)) || widget->property("ralleurDialogManaged").toBool()) return;
    // Respect applications which supply their own dialog styling.
    if (!widget->styleSheet().isEmpty()) return;
    widget->setProperty("ralleurDialogManaged", true);
    if (qobject_cast<QMenu *>(widget)) {
        widget->setProperty("ralleurMenuWasTranslucent", widget->testAttribute(Qt::WA_TranslucentBackground));
        widget->setAttribute(Qt::WA_TranslucentBackground);
    }
    widget->installEventFilter(this);
    // Menus must be styled before popup() maps their native surface. Applying
    // a stylesheet later can hide a Wayland popup while recreating its surface.
    if (qobject_cast<QMenu *>(widget)) { apply(widget); return; }
    // Stylesheet changes during polish can reenter Qt's polish machinery.
    QPointer<QWidget> guarded(widget);
    QTimer::singleShot(0, this, [this, guarded] {
        if (guarded && guarded->property("ralleurDialogManaged").toBool()) apply(guarded);
    });
}

void RalleurDialogStyle::unpolish(QWidget *widget)
{
    if (widget->property("ralleurDialogManaged").toBool() && !widget->property("ralleurDialogUpdating").toBool()) {
        widget->removeEventFilter(this);
        widget->setProperty("ralleurDialogManaged", false);
        if (qobject_cast<QMenu *>(widget)) widget->setAttribute(Qt::WA_TranslucentBackground, widget->property("ralleurMenuWasTranslucent").toBool());
        widget->setStyleSheet({});
    }
    QProxyStyle::unpolish(widget);
}

bool RalleurDialogStyle::eventFilter(QObject *object, QEvent *event)
{
    if (event->type() == QEvent::Show || event->type() == QEvent::ApplicationPaletteChange) {
        if (auto widget = qobject_cast<QWidget *>(object)) apply(widget);
    }
    return false;
}

void RalleurDialogStyle::apply(QWidget *dialog)
{
    if (dialog->property("ralleurGlassMenu").toBool()) return;
    if (qobject_cast<QMessageBox *>(dialog) && dialog->layout()) {
        dialog->layout()->setContentsMargins(28, 28, 28, 24);
        dialog->layout()->setSpacing(16);
        const int available = dialog->screen()->availableGeometry().width() - 48;
        dialog->setMinimumWidth(qMin(580, qMax(240, available)));
    }
    const bool dark = qApp->palette().color(QPalette::Window).lightness() < 128;
    const QString bg = dark ? "#1c1f21" : "#f8f6f3";
    const QString fg = dark ? "#f4f3f1" : "#161616";
    const QString muted = dark ? "#adb0b3" : "#666870";
    const QString border = dark ? "#45484b" : "#d9d7d5";
    const QString button = dark ? "#282b2e" : "#f2f0ed";
    const QString hover = dark ? "#363a3e" : "#e8e5e1";
    // Button roles come from Qt, never from localized captions. Ordinary
    // confirmation buttons are neutral; destructive actions use coral in dark.
    for (auto box : dialog->findChildren<QDialogButtonBox *>()) {
        for (auto abstract : box->buttons()) {
            auto push = qobject_cast<QPushButton *>(abstract);
            if (!push) continue;
            const auto role = box->buttonRole(push);
            const bool destructive = role == QDialogButtonBox::DestructiveRole;
            const bool primary = destructive || role == QDialogButtonBox::AcceptRole || role == QDialogButtonBox::YesRole;
            QString caption = push->text(); caption.remove('&');
            const int iconWidth = push->icon().isNull() ? 0 : push->iconSize().width() + 8;
            push->setMinimumWidth(qMax(112, push->fontMetrics().horizontalAdvance(caption) + iconWidth + 48));
            push->setProperty("ralleurAction", destructive && dark ? "destructive" : primary ? "primary" : "secondary");
        }
    }
    // QMessageBox exposes these names; normal file/settings labels retain
    // their original hierarchy and spacing.
    const QString css = qobject_cast<QMenu *>(dialog) ? QStringLiteral(R"(
QMenu { background: %1; color: %2; border: 1px solid %3; border-radius: 14px; padding: 8px; }
QMenu::item { padding: 10px 22px 10px 12px; border: 1px solid transparent; border-radius: 9px; }
QMenu::item:selected { background: %4; }
QMenu::item:disabled { color: %5; }
QMenu::separator { height: 1px; background: %3; margin: 8px 10px; }
QMenu::icon { margin-left: 8px; }
)").arg(bg, fg, border, dark ? "#2b3544" : "#e4e2df", muted) : QStringLiteral(R"(
QDialog { background: %1; color: %2; }
QDialog QLabel, QDialog QCheckBox, QDialog QRadioButton, QDialog QGroupBox { color: %2; }
QDialog QLabel#qt_msgbox_label { font-size: 20px; font-weight: 600; padding: 8px 0; }
QDialog QLabel#qt_msgbox_informativelabel { color: %3; font-size: 14px; padding-bottom: 16px; }
QDialog QDialogButtonBox { padding-top: 16px; }
QDialog QPushButton { background: %5; color: %2; border: 1px solid %4; border-radius: 19px; min-height: 20px; min-width: 80px; padding: 8px 20px; }
QDialog QPushButton:hover { background: %6; }
QDialog QPushButton[ralleurAction="primary"] { background: %2; color: %1; border-color: %2; }
QDialog QPushButton[ralleurAction="primary"]:hover { background: %3; }
QDialog QPushButton[ralleurAction="destructive"] { background: #ff7066; color: #151719; border-color: #ff7066; }
QDialog QPushButton[ralleurAction="destructive"]:hover { background: #ff8b82; }
QDialog QPushButton:focus { border: 2px solid #648fc5; padding: 7px 19px; }
QDialog QPushButton:pressed { border: 2px solid %3; padding: 7px 19px; }
QDialog QPushButton:disabled { color: %3; background: %5; border-color: %4; }
QDialog QCheckBox { spacing: 10px; padding: 6px 0; }
)").arg(bg, fg, muted, border, button, hover);
    if (dialog->styleSheet() != css) {
        dialog->setProperty("ralleurDialogUpdating", true);
        dialog->setStyleSheet(css);
        dialog->setProperty("ralleurDialogUpdating", false);
    }
}
