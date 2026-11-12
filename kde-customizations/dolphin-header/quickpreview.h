// SPDX-License-Identifier: MIT
#pragma once
#include <QObject>
#include <QPointer>
#include <QHash>
#include <KFileItem>
#include <QUrl>

class QDialog;
class QMainWindow;
class QWidget;

namespace Ralleur {
class QuickPreview : public QObject {
    Q_OBJECT
public:
    explicit QuickPreview(QMainWindow *window);
    void bindViews();
protected:
    bool eventFilter(QObject *watched, QEvent *event) override;
private Q_SLOTS:
    void selectionChanged(const KFileItemList &items);
private:
    void toggle(QWidget *view);
    void updatePreview(const KFileItemList &items);
    QPointer<QMainWindow> m_window;
    QPointer<QDialog> m_dialog;
    QPointer<QWidget> m_view;
    QUrl m_previewUrl;
    QHash<QObject *, KFileItemList> m_selection;
};
}
