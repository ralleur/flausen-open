pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services

StyledRect {
    id: root

    required property PopoutState popouts
    property bool _isSidebarOpen: false
    property real scaleOffset: 1.0
    property real fontScale: 1.0

    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    property date viewDate: new Date()
    // Follow the shell clock across midnight, including a day when this stays open.
    readonly property date today: Time.date
    readonly property int currMonth: viewDate.getMonth()
    readonly property int currYear: viewDate.getFullYear()
    readonly property var calendarLocale: SystemLanguage.timeLocale
    readonly property int leadingDays: (new Date(currYear, currMonth, 1).getDay() - calendarLocale.firstDayOfWeek + 7) % 7
    readonly property real inset: 18 * root.scaleOffset
    readonly property real verticalInset: 6 * root.scaleOffset
    readonly property real cellHeight: Math.max(44 * root.scaleOffset, bodyPointSize * 4 / 3 * 2.4)

    function shiftMonth(delta: int): void {
        root.viewDate = new Date(root.currYear, root.currMonth + delta, 1);
    }

    function goToToday(): void {
        root.viewDate = new Date(root.today);
    }

    implicitWidth: 497 * root.scaleOffset
    implicitHeight: inner.implicitHeight + root.verticalInset * 2
    radius: Tokens.rounding.extraLarge * root.scaleOffset
    // ClipWrapper owns the glass: avoid a second, milky card over the blur.
    color: "transparent"

    CalendarMonthSlide {
        id: monthSlide
        shownDate: root.viewDate
        offset: Tokens.padding.extraLarge * root.scaleOffset
    }

    CustomMouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.MiddleButton | Qt.RightButton
        onWheel: event => {
            if (event.angleDelta.y !== 0)
                root.shiftMonth(event.angleDelta.y > 0 ? -1 : 1);
        }
        onClicked: mouse => {
            if (mouse.button === Qt.MiddleButton)
                root.goToToday();
            else if (mouse.button === Qt.RightButton)
                root.popouts.currentName = "clockcontext";
        }
    }

    component HeaderButton: Button {
        id: control
        property string symbol: ""
        property string description: text
        implicitWidth: symbol ? implicitHeight : label.implicitWidth + 28 * root.scaleOffset
        implicitHeight: Math.max(34 * root.scaleOffset, label.implicitHeight + 10 * root.scaleOffset)
        Layout.alignment: Qt.AlignTop
        Layout.topMargin: 6 * root.scaleOffset
        hoverEnabled: true
        Accessible.name: description
        ToolTip.visible: hovered
        ToolTip.text: description
        ToolTip.delay: 700
        background: Rectangle {
            radius: height / 2
            color: control.down ? MenuStyle.rule : control.hovered || control.visualFocus ? MenuStyle.cardFill : "transparent"
            border.width: 1
            border.color: control.visualFocus ? MenuStyle.accent : MenuStyle.border
        }
        contentItem: Item {
            implicitWidth: label.implicitWidth
            implicitHeight: label.implicitHeight
            MenuText {
                id: label
                anchors.centerIn: parent
                visible: !control.symbol
                text: control.text
                font.pointSize: root.bodyPointSize
            }
            Canvas {
                anchors.centerIn: parent
                visible: !!control.symbol
                width: 16 * root.scaleOffset
                height: 16 * root.scaleOffset
                property color ink: MenuStyle.ink
                onInkChanged: requestPaint()
                onPaint: {
                    const ctx = getContext("2d");
                    ctx.reset();
                    ctx.strokeStyle = ink;
                    ctx.lineWidth = 1.8 * root.scaleOffset;
                    ctx.lineCap = "round";
                    ctx.lineJoin = "round";
                    const left = control.symbol === "chevron_left";
                    ctx.beginPath();
                    ctx.moveTo(width * (left ? 0.65 : 0.35), height * 0.2);
                    ctx.lineTo(width * (left ? 0.35 : 0.65), height * 0.5);
                    ctx.lineTo(width * (left ? 0.65 : 0.35), height * 0.8);
                    ctx.stroke();
                }
            }
        }
    }

    ColumnLayout {
        id: inner
        x: root.inset
        y: root.verticalInset
        width: root.width - root.inset * 2
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.bottomMargin: 8 * root.scaleOffset
            spacing: 10 * root.scaleOffset

            MenuText {
                id: monthYearDisplay
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                text: root.calendarLocale.toString(root.viewDate, "MMMM yyyy")
                font.pointSize: root.bodyPointSize * 2.06
                font.weight: Font.Bold
                Layout.alignment: Qt.AlignTop
                Layout.topMargin: 3 * root.scaleOffset
                wrapMode: Text.WordWrap
                opacity: monthSlide.animOpacity
            }
            HeaderButton {
                text: qsTr("Today")
                description: qsTr("Go to today")
                onClicked: root.goToToday()
            }
            HeaderButton {
                symbol: "chevron_left"
                description: qsTr("Previous month")
                onClicked: root.shiftMonth(-1)
            }
            HeaderButton {
                symbol: "chevron_right"
                description: qsTr("Next month")
                onClicked: root.shiftMonth(1)
            }
        }

        Row {
            id: weekdays
            Layout.leftMargin: -10 * root.scaleOffset
            Layout.rightMargin: -10 * root.scaleOffset
            Layout.fillWidth: true
            Layout.preferredHeight: 32 * root.scaleOffset
            Repeater {
                model: 7
                MenuText {
                    required property int index
                    width: weekdays.width / 7
                    height: 32 * root.scaleOffset
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    text: root.calendarLocale.standaloneDayName((root.calendarLocale.firstDayOfWeek + index) % 7, Locale.ShortFormat)
                    font.pointSize: root.bodyPointSize
                    color: [0, 6].includes((root.calendarLocale.firstDayOfWeek + index) % 7) ? MenuStyle.muted : MenuStyle.ink
                }
            }
        }

        Grid {
            id: grid
            Layout.leftMargin: -10 * root.scaleOffset
            Layout.rightMargin: -10 * root.scaleOffset
            Layout.fillWidth: true
            Layout.preferredHeight: root.cellHeight * 6
            columns: 7
            opacity: monthSlide.animOpacity
            transform: Translate { x: monthSlide.animTranslate }

            Repeater {
                model: 42
                delegate: Item {
                    id: dayItem
                    required property int index
                    readonly property date date: new Date(root.currYear, root.currMonth, 1 - root.leadingDays + index)
                    readonly property bool isToday: date.getFullYear() === root.today.getFullYear()
                        && date.getMonth() === root.today.getMonth() && date.getDate() === root.today.getDate()
                    readonly property bool inMonth: date.getMonth() === root.currMonth
                    width: grid.width / 7
                    height: root.cellHeight
                    Accessible.role: Accessible.StaticText
                    Accessible.name: root.calendarLocale.toString(date, Locale.LongFormat)

                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(parent.width - 4 * root.scaleOffset, 38 * root.scaleOffset * Math.max(1, root.fontScale / 1.15))
                        height: width
                        radius: width / 2
                        visible: dayItem.isToday
                        color: MenuStyle.accent
                        PrimaryControlFill {} // Capture primary material
                    }
                    MenuText {
                        anchors.centerIn: parent
                        text: root.calendarLocale.toString(dayItem.date.getDate())
                        font.pointSize: root.bodyPointSize * 1.25
                        color: dayItem.isToday ? "white" : [0, 6].includes(dayItem.date.getDay()) ? MenuStyle.muted : MenuStyle.ink
                        opacity: dayItem.isToday || dayItem.inMonth ? 1 : 0.4
                    }
                }
            }
        }
    }
}
