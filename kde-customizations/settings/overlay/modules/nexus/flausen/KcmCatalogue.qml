pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import Quickshell
import Flausen.Settings
import qs.modules.nexus
Item {
    id:root
    required property NexusState nState
    readonly property var modules: metadata.catalogue()
    readonly property var filtered: modules.filter(m => (m.name + " " + m.description).toLowerCase().includes(search.text.trim().toLowerCase()))
    KcmHost {id:metadata;visible:false}
    ColumnLayout {
        anchors.fill:parent
        spacing:16
        C.TextField {id:search;Layout.fillWidth:true;placeholderText:qsTranslate("Flausen", "Search all system settings");Accessible.name:placeholderText}
        C.ScrollView {
            Layout.fillWidth:true;Layout.fillHeight:true
            contentWidth:availableWidth
            ColumnLayout {
                width:parent.width
                spacing:8
                Repeater {
                    model:root.filtered
                    C.Button {
                        id:row
                        required property var modelData
                        text:modelData.name
                        Layout.fillWidth:true
                        implicitHeight:Math.max(70,labels.implicitHeight+28)
                        leftPadding:18;rightPadding:18;topPadding:14;bottomPadding:14
                        onClicked:root.nState.openSystemModule(modelData.id,modelData.name)
                        background:Rectangle {radius:14;color:row.hovered ? FlausenStyle.selected : FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
                        contentItem:RowLayout {
                            spacing:16
                            Image {source:Quickshell.iconPath(row.modelData.icon);Layout.preferredWidth:48;Layout.preferredHeight:48;Layout.alignment:Qt.AlignVCenter;sourceSize.width:Math.ceil(48*Screen.devicePixelRatio);sourceSize.height:Math.ceil(48*Screen.devicePixelRatio);fillMode:Image.PreserveAspectFit;smooth:true;mipmap:true}
                            ColumnLayout {
                                id:labels
                                Layout.fillWidth:true
                                spacing:4
                                Text {text:row.modelData.name;color:FlausenStyle.text;font:FlausenStyle.typeface(14);Layout.fillWidth:true;wrapMode:Text.WordWrap}
                                Text {text:row.modelData.description;visible:text.length>0;color:FlausenStyle.secondary;font:FlausenStyle.typeface(12);Layout.fillWidth:true;wrapMode:Text.WordWrap}
                            }
                            SettingsIcon {name:"chevron_right";color:FlausenStyle.secondary;fieldSize:24;glyphPixels:24;Layout.alignment:Qt.AlignVCenter;Layout.preferredWidth:24;Layout.preferredHeight:24}
                        }
                    }
                }
                Text {visible:root.filtered.length===0;text:qsTranslate("Flausen", "No matching settings found.");color:FlausenStyle.secondary;font:FlausenStyle.typeface(14);Layout.topMargin:20}
            }
        }
    }
}
