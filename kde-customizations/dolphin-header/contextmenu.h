// SPDX-License-Identifier: MIT
#pragma once
#include <QObject>
#include <QPointer>
#include <QSet>
#include <QList>
class QLocalSocket;
class QMenu;
class QWidget;
namespace Ralleur {
class ContextGlass;
class ContextMenus : public QObject {
public:
    explicit ContextMenus(QObject *parent = nullptr);
    static void prepare(QMenu *menu, bool shift);
    static void styleMenu(QMenu *menu);
    static void setShift(QMenu *menu, bool shift);
protected:
    bool eventFilter(QObject *watched, QEvent *event) override;
private:
    void syncBackdrop();
    bool belongsToContext(QMenu *menu) const;
    QLocalSocket *m_socket;
    QSet<QMenu *> m_visible;
    QPointer<QMenu> m_active;
    QList<QPointer<ContextGlass>> m_glass;
    void syncGlass(QMenu *menu);
    void prewarmGlass(QWidget *window);
};
}
