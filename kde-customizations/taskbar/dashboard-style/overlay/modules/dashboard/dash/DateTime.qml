pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services

Item {
    id: root

    anchors.top: parent.top
    anchors.bottom: parent.bottom
    implicitWidth: Tokens.sizes.dashboard.dateTimeWidth

    ColumnLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        spacing: 0

        MenuText {
            Layout.bottomMargin: -(font.pointSize * 0.4)
            Layout.alignment: Qt.AlignHCenter
            text: Time.hourStr
            color: Colours.palette.m3secondary
            font: MenuStyle.withSystemFamily(Tokens.font.clock.size(28).weight(Font.DemiBold).build())
        }

        MenuText {
            Layout.alignment: Qt.AlignHCenter
            text: "•••"
            color: Colours.palette.m3primary
            font: MenuStyle.withSystemFamily(Tokens.font.clock.size(28 * 0.9).build())
        }

        MenuText {
            Layout.topMargin: -(font.pointSize * 0.4)
            Layout.alignment: Qt.AlignHCenter
            text: Time.minuteStr
            color: Colours.palette.m3secondary
            font: MenuStyle.withSystemFamily(Tokens.font.clock.size(28).weight(Font.DemiBold).build())
        }

        Loader {
            Layout.topMargin: -(((item as MenuText)?.font.pointSize ?? 0) * 0.4)
            Layout.alignment: Qt.AlignHCenter
            asynchronous: true
            active: Config.dashboard.showClockSeconds
            visible: active

            sourceComponent: MenuText {
                text: "•••"
                color: Colours.palette.m3primary
                font: MenuStyle.withSystemFamily(Tokens.font.clock.size(28 * 0.9).build())
            }
        }

        Loader {
            Layout.topMargin: -(((item as MenuText)?.font.pointSize ?? 0) * 0.4)
            Layout.alignment: Qt.AlignHCenter
            asynchronous: true
            active: Config.dashboard.showClockSeconds
            visible: active

            sourceComponent: MenuText {
                text: Time.format("ss")
                color: Colours.palette.m3secondary
                font: MenuStyle.withSystemFamily(Tokens.font.clock.size(28).weight(Font.DemiBold).build())
            }
        }

        Loader {
            asynchronous: true
            Layout.alignment: Qt.AlignHCenter

            active: Units.twelveHourClock
            visible: active

            sourceComponent: MenuText {
                text: Time.amPmStr
                color: Colours.palette.m3primary
                font: MenuStyle.withSystemFamily(Tokens.font.clock.size(18).weight(Font.DemiBold).build())
            }
        }
    }
}
