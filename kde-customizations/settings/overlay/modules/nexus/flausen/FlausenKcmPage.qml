pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import Flausen.Settings
import qs.modules.nexus
Item {
    id:root
    required property NexusState nState
    property bool continueAfterSave:false
    readonly property alias backend: host
    readonly property var moduleActions: host.page?.actions ?? []
    function saveAndContinue(): void {
        continueAfterSave=true;
        host.save();
        if(!host.needsSave) {continueAfterSave=false;root.nState.finishPending();}
    }
    function discardAndContinue(): void {host.reset();root.nState.finishPending();}
    ColumnLayout {
        anchors.fill:parent
        spacing:20
        RowLayout {
            Layout.fillWidth:true
            FlausenButton {text:qsTranslate("Flausen", "‹ Back");onClicked:host.depth>1 ? host.back() : root.nState.backFromSystemModule()}
            Text {text:host.depth>1 && host.page?.title ? host.page.title : root.nState.systemTitle;Layout.fillWidth:true;elide:Text.ElideRight;font:FlausenStyle.typeface(26);color:FlausenStyle.text}
        }
        Flow {
            Layout.fillWidth:true
            Layout.preferredHeight: visible ? implicitHeight : 0
            spacing:8
            visible:root.moduleActions.some(action => action.visible !== false)
            Repeater {
                model:root.moduleActions
                FlausenButton {
                    id: actionButton
                    required property var modelData
                    visible:modelData.visible !== false
                    enabled:modelData.enabled
                    text:modelData.text.replace(/&([^&])/g,"$1").replace(/&&/g,"&")
                    onClicked: (modelData.children?.length ?? 0)>0 ? actionMenu.popup() : modelData.trigger()
                    C.Menu {
                        id:actionMenu
                        background:Rectangle {color:FlausenStyle.card;radius:12;border.width:1;border.color:FlausenStyle.line}
                        Repeater {
                            model:actionButton.modelData.children ?? []
                            C.MenuItem {required property var modelData;action:modelData;font:FlausenStyle.typeface(14)}
                        }
                    }
                }
            }
        }
        C.Pane {
            id:surface
            Layout.fillWidth:true;Layout.fillHeight:true
            padding:16
            font:FlausenStyle.typeface(14)
            palette {
                window:FlausenStyle.surface;windowText:FlausenStyle.text
                base:FlausenStyle.card;text:FlausenStyle.text
                button:FlausenStyle.card;buttonText:FlausenStyle.text
                highlight:FlausenStyle.accent;highlightedText:"white"
                mid:FlausenStyle.line;light:FlausenStyle.line;dark:FlausenStyle.line
            }
            Kirigami.Theme.inherit:false
            Kirigami.Theme.backgroundColor:FlausenStyle.surface
            Kirigami.Theme.textColor:FlausenStyle.text
            Kirigami.Theme.highlightColor:FlausenStyle.accent
            Kirigami.Theme.highlightedTextColor:"white"
            Kirigami.Theme.linkColor:FlausenStyle.accent
            Kirigami.Theme.disabledTextColor:FlausenStyle.secondary
            background:Rectangle {color:"transparent"}
            KcmHost {
                id:host
                anchors.fill:parent
                visible:root.nState.systemModule.charAt(0)!=="@"
                moduleId:visible ? root.nState.systemModule : ""
                onChanged: {
                    root.nState.systemDirty=needsSave;
                    if(root.continueAfterSave && !needsSave){root.continueAfterSave=false;root.nState.finishPending();}
                }
                onCloseBlocked:root.nState.requestExit()
            }
            KcmSkin {anchors.fill:parent;targetItem:host.page;moduleKey:root.nState.systemModule;visible:host.visible}
            Loader {
                anchors.fill:parent
                active:root.nState.systemModule.charAt(0)==="@"
                sourceComponent:root.nState.systemModule==="@clock" ? clock : catalogue
            }
            Component {id:clock;TimeDatePage {}}
            Component {id:catalogue;KcmCatalogue {nState:root.nState}}
            ColumnLayout {
                visible:host.visible && host.error.length>0
                anchors.centerIn:parent
                width:Math.min(parent.width,500)
                spacing:16
                Text {text:qsTranslate("Flausen", "This page could not be loaded.");font:FlausenStyle.typeface(18);color:FlausenStyle.text;wrapMode:Text.WordWrap;Layout.fillWidth:true}
                Text {text:host.error;font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;wrapMode:Text.WordWrap;Layout.fillWidth:true}
                FlausenButton {text:qsTranslate("Flausen", "Back to overview");onClicked:root.nState.backFromSystemModule()}
            }
        }
        Rectangle {Layout.fillWidth:true;implicitHeight:1;color:FlausenStyle.line;visible:host.visible && host.ready}
        RowLayout {
            visible:host.visible && host.ready
            Layout.fillWidth:true
            spacing:10
            FlausenButton {text:qsTranslate("Flausen", "Defaults");visible:host.canDefault;onClicked:host.defaults()}
            Text {text:host.needsSave ? qsTranslate("Flausen", "Unsaved changes") : qsTranslate("Flausen", "Settings up to date");color:FlausenStyle.secondary;font:FlausenStyle.typeface(12);Layout.fillWidth:true;elide:Text.ElideRight}
            FlausenButton {text:qsTranslate("Flausen", "Reset");enabled:host.needsSave;onClicked:host.reset()}
            FlausenButton {text:qsTranslate("Flausen", "Apply");enabled:host.needsSave;onClicked:host.save()}
        }
    }
}
