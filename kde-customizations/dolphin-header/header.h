// SPDX-License-Identifier: MIT
#pragma once
#include <QObject>
#include <QPointer>

class QMainWindow;
class QToolBar;
class QToolButton;
class QWidgetAction;
class KWindowShadow;

namespace Ralleur {
class FolderColors;
class QuickPreview;

class Header : public QObject {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.ralleur.DolphinHeader")
    Q_PROPERTY(bool maximized READ maximized)
    Q_PROPERTY(bool decorated READ decorated)
    Q_PROPERTY(bool shadowCreated READ shadowCreated)
    Q_PROPERTY(int alphaBufferSize READ alphaBufferSize)
public:
    explicit Header(QWidget *window, QToolBar *toolbar);
    bool maximized() const;
    bool decorated() const;
    bool shadowCreated() const;
    int alphaBufferSize() const;
    void ensureControls();
public Q_SLOTS:
    void minimize();
    void maximizeRestore();
    void closeWindow();
protected:
    bool eventFilter(QObject *watched, QEvent *event) override;
private:
    void updateFrame();
    void createShadow();
    void configureContents();
    Qt::Edges resizeEdges(const QPointF &position) const;
    QPointer<QWidget> m_window;
    QPointer<QToolBar> m_toolbar;
    QPointer<QWidgetAction> m_action;
    QPointer<QToolButton> m_minimize;
    QPointer<QToolButton> m_maximize;
    QPointer<QToolButton> m_close;
    KWindowShadow *m_shadow = nullptr;
    bool m_adjusting = false;
    bool m_contentsPending = false;
    FolderColors *m_colors = nullptr;
    QuickPreview *m_preview = nullptr;
};

class Integration : public QObject {
    Q_OBJECT
public:
    explicit Integration(QObject *parent = nullptr);
    static bool eligible(QMainWindow *window);
    static Header *attach(QMainWindow *window);
    static Header *attachFileDialog(QWidget *window);
    void start();
protected:
    bool eventFilter(QObject *watched, QEvent *event) override;
};
}
