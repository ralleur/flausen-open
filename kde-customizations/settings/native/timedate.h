// SPDX-License-Identifier: GPL-3.0-only
#pragma once
#include <QObject>
#include <QTimer>
#include <QVariantMap>
#include <qqmlintegration.h>
class TimeDate:public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString timezone READ timezone NOTIFY changed)
    Q_PROPERTY(bool ntp READ ntp NOTIFY changed)
    Q_PROPERTY(bool canNtp READ canNtp NOTIFY changed)
    Q_PROPERTY(bool available READ available NOTIFY changed)
    Q_PROPERTY(bool busy READ busy NOTIFY changed)
    Q_PROPERTY(QString error READ error NOTIFY changed)
    Q_PROPERTY(QString localTime READ localTime NOTIFY tick)
    Q_PROPERTY(QStringList timezones READ timezones CONSTANT)
public:
    explicit TimeDate(QObject *parent=nullptr);
    QString timezone()const{return m_timezone;}
    bool ntp()const{return m_ntp;}
    bool canNtp()const{return m_canNtp;}
    bool available()const{return m_available;}
    bool busy()const{return m_busy;}
    QString error()const{return m_error;}
    QString localTime()const;
    QStringList timezones()const;
    Q_INVOKABLE void refresh();
    Q_INVOKABLE void setTimezone(const QString &zone);
    Q_INVOKABLE void setNtp(bool enabled);
    Q_INVOKABLE void setLocalTime(const QString &date,const QString &time);
signals:
    void changed();void tick();
private slots:
    void propertiesChanged(const QString &,const QVariantMap &,const QStringList &);
private:
    void call(const QString &method,const QVariantList &args);
    QString m_timezone,m_error;
    bool m_ntp=false,m_canNtp=false,m_available=false,m_busy=false;
    QTimer m_timer;
};
