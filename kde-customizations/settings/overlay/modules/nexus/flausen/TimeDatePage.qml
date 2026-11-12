pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import Flausen.Settings
Item {
    id: root
    readonly property string selectedZone: zones.editText || zones.currentText
    readonly property TimeDate backend: TimeDate { id: timeDate }
    C.ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        ColumnLayout {
            width:parent.width
            spacing:16
            Text {text:timeDate.localTime;color:FlausenStyle.text;font:FlausenStyle.typeface(22);Layout.fillWidth:true;wrapMode:Text.WordWrap;Layout.bottomMargin:12}
            Rectangle {
                Layout.fillWidth:true;implicitHeight:90;radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line
                FlausenSwitch {
                    anchors.fill:parent
                    text:qsTranslate("Flausen", "Set date & time automatically")
                    checked:timeDate.ntp
                    enabled:timeDate.available && timeDate.canNtp && !timeDate.busy
                    onToggled:timeDate.setNtp(checked)
                }
            }
            Text {text:qsTranslate("Flausen", "Time zone");font:FlausenStyle.typeface(17);color:FlausenStyle.text}
            C.ComboBox {
                id: zones
                Layout.fillWidth:true
                model:timeDate.timezones
                editable:true
                currentIndex:model.indexOf(timeDate.timezone)
                enabled:timeDate.available && !timeDate.busy
                onAccepted: if (find(editText) >= 0) currentIndex=find(editText)
            }
            FlausenButton {text:timeDate.busy ? qsTranslate("Flausen", "Applying …") : qsTranslate("Flausen", "Apply time zone");enabled:timeDate.available && !timeDate.busy && root.selectedZone !== timeDate.timezone;onClicked:timeDate.setTimezone(root.selectedZone)}
            Text {text:qsTranslate("Flausen", "Set manually");font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.topMargin:16}
            Text {text:qsTranslate("Flausen", "Turn off automatic synchronization to set the time manually.");font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;wrapMode:Text.WordWrap;Layout.fillWidth:true}
            RowLayout {
                Layout.fillWidth:true
                C.TextField {id:dateInput;Layout.fillWidth:true;placeholderText:qsTranslate("Flausen", "YYYY-MM-DD");Accessible.name:qsTranslate("Flausen", "Date in year-month-day format");enabled:!timeDate.ntp && !timeDate.busy}
                C.TextField {id:timeInput;Layout.fillWidth:true;placeholderText:"HH:MM";Accessible.name:qsTranslate("Flausen", "Time in 24-hour format");enabled:!timeDate.ntp && !timeDate.busy}
            }
            FlausenButton {text:qsTranslate("Flausen", "Apply date & time");enabled:timeDate.available && !timeDate.ntp && !timeDate.busy && dateInput.text.length>0 && timeInput.text.length>0;onClicked:timeDate.setLocalTime(dateInput.text,timeInput.text)}
            Text {visible:timeDate.error.length>0;text:timeDate.error;color:FlausenStyle.secondary;font:FlausenStyle.typeface(13);wrapMode:Text.WordWrap;Layout.fillWidth:true}
            Text {text:qsTranslate("Flausen", "Changes may require system authorization.");color:FlausenStyle.secondary;font:FlausenStyle.typeface(12);Layout.topMargin:12}
        }
    }
    KcmSkin {anchors.fill:parent;targetItem:root.children[0]}
}
