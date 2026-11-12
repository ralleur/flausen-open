// SPDX-License-Identifier: MIT
#pragma once
#include <QQuickItem>
#include <QPointer>
#include <QUrl>
#include <QVariantMap>
#include <qqmlintegration.h>
#include <QDBusMessage>
class PicturePicker : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(bool opened READ opened NOTIFY openedChanged)
    Q_PROPERTY(QUrl selectedFile READ selectedFile NOTIFY accepted)
    Q_PROPERTY(QString error READ error NOTIFY failed)
public:
    explicit PicturePicker(QQuickItem *parent = nullptr);
    ~PicturePicker() override;
    bool opened() const { return m_open; }
    QUrl selectedFile() const { return m_selected; }
    QString error() const { return m_error; }
    Q_INVOKABLE void open();
    Q_INVOKABLE void reject();
signals:
    void openedChanged();
    void accepted();
    void failed();
private slots:
    void response(uint code, const QVariantMap &results, const QDBusMessage &message);
private:
    void request(const QString &parentHandle);
    void finish();
    void fail(const QString &message);
    bool m_open = false;
    QUrl m_selected;
    QString m_path, m_error;
    QPointer<QQuickWindow> m_exported;
};
