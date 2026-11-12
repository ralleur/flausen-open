// SPDX-License-Identifier: MIT
#pragma once
#include <QQuickItem>
#include <QPointer>
#include <qqmlintegration.h>
class KWindowShadow;
class QQuickWindow;
class WindowFrame : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(bool shadowCreated READ shadowCreated NOTIFY changed)
public:
    explicit WindowFrame(QQuickItem *parent = nullptr);
    bool shadowCreated() const;
signals:
    void changed();
protected:
    bool eventFilter(QObject *object, QEvent *event) override;
private:
    void attach(QQuickWindow *window);
    void updateFrame();
    QPointer<QQuickWindow> m_window;
    KWindowShadow *m_shadow = nullptr;
};
