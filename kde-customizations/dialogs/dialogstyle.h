// SPDX-License-Identifier: MIT
#pragma once
#include <QProxyStyle>

class RalleurDialogStyle : public QProxyStyle {
    Q_OBJECT
public:
    explicit RalleurDialogStyle(QStyle *base = nullptr);
    int styleHint(StyleHint hint, const QStyleOption *option = nullptr, const QWidget *widget = nullptr, QStyleHintReturn *data = nullptr) const override;
    void drawComplexControl(ComplexControl control, const QStyleOptionComplex *option, QPainter *painter, const QWidget *widget = nullptr) const override;
    void polish(QWidget *widget) override;
    void unpolish(QWidget *widget) override;
protected:
    bool eventFilter(QObject *object, QEvent *event) override;
private:
    void apply(QWidget *dialog);
};
