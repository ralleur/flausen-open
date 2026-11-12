#include <KLocalizedString>
// SPDX-License-Identifier: GPL-3.0-only
#include "timedate.h"
#include <QDBusConnection>
#include <QDBusInterface>
#include <QDBusPendingCallWatcher>
#include <QDBusPendingReply>
#include <QDBusMessage>
#include <QDBusVariant>
#include <QDateTime>
#include <QTimeZone>
#include <QLocale>
static constexpr auto service="org.freedesktop.timedate1";
static constexpr auto path="/org/freedesktop/timedate1";
TimeDate::TimeDate(QObject *parent):QObject(parent){
    m_timer.setInterval(1000);connect(&m_timer,&QTimer::timeout,this,&TimeDate::tick);m_timer.start();
    QDBusConnection::systemBus().connect(service,path,"org.freedesktop.DBus.Properties","PropertiesChanged",this,SLOT(propertiesChanged(QString,QVariantMap,QStringList)));
    refresh();
}
QString TimeDate::localTime()const{return QLocale().toString(QDateTime::currentDateTime().toTimeZone(QTimeZone(m_timezone.toUtf8())),"dddd, MMMM d, yyyy · HH:mm:ss");}
QStringList TimeDate::timezones()const{QStringList zones;for(auto z:QTimeZone::availableTimeZoneIds())zones<<QString::fromUtf8(z);return zones;}
void TimeDate::propertiesChanged(const QString &iface,const QVariantMap &,const QStringList &){if(iface==service)refresh();}
void TimeDate::refresh(){
    auto message=QDBusMessage::createMethodCall(service,path,"org.freedesktop.DBus.Properties","GetAll");message<<QString(service);
    auto *watcher=new QDBusPendingCallWatcher(QDBusConnection::systemBus().asyncCall(message),this);
    connect(watcher,&QDBusPendingCallWatcher::finished,this,[this,watcher]{
        QDBusPendingReply<QVariantMap> reply=*watcher;
        m_available=!reply.isError();
        if(reply.isError())m_error=reply.error().message();
        else {auto p=reply.value();m_timezone=p.value("Timezone").toString();m_ntp=p.value("NTP").toBool();m_canNtp=p.value("CanNTP").toBool();}
        emit changed();emit tick();watcher->deleteLater();
    });
}
void TimeDate::call(const QString &method,const QVariantList &args){
    if(m_busy)return;m_busy=true;m_error.clear();emit changed();
    auto message=QDBusMessage::createMethodCall(service,path,service,method);message.setArguments(args);
    auto *watcher=new QDBusPendingCallWatcher(QDBusConnection::systemBus().asyncCall(message,120000),this);
    connect(watcher,&QDBusPendingCallWatcher::finished,this,[this,watcher]{
        QDBusPendingReply<> reply=*watcher;m_busy=false;
        if(reply.isError())m_error=reply.error().message();
        emit changed();refresh();watcher->deleteLater();
    });
}
void TimeDate::setTimezone(const QString &zone){
    if(!QTimeZone::isTimeZoneIdAvailable(zone.toUtf8())){m_error=i18nd("flausen", "Please select a valid time zone.");emit changed();return;}
    call("SetTimezone",{zone,true});
}
void TimeDate::setNtp(bool enabled){call("SetNTP",{enabled,true});}
void TimeDate::setLocalTime(const QString &date,const QString &time){
    auto dt=QDateTime(QDate::fromString(date,"yyyy-MM-dd"),QTime::fromString(time,"HH:mm"),QTimeZone(m_timezone.toUtf8()));
    if(!dt.isValid() || m_ntp){m_error=i18nd("flausen", "Enter a valid date and time and disable automatic time synchronization.");emit changed();return;}
    call("SetTime",{QVariant::fromValue<qlonglong>(dt.toMSecsSinceEpoch()*1000),false,true});
}
