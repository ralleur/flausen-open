pragma ComponentBehavior: Bound

import QtQuick
import qs.modules.nexus.flausen
import QtQuick.Layouts
import Quickshell
import Quickshell.Services.Pipewire
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils
import qs.modules.nexus.common

PageBase {
    id: root

    title: qsTr("App volumes")
    isSubPage: true

    ColumnLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        width: root.cappedWidth
        spacing: 8

        StyledText {
            Layout.fillWidth: true
            Layout.leftMargin: Tokens.padding.small
            Layout.bottomMargin: Tokens.spacing.medium
            text: qsTr("Adjust the volume of individual apps currently playing audio.")
            color: FlausenStyle.secondary
            font: FlausenStyle.typeface(14)
            wrapMode: Text.WordWrap
        }

        ItemList {
            id: streamList

            first: true
            last: true
            showList: true
            placeholderIcon: "music_off"
            placeholderText: qsTr("No apps playing audio")
            color: list.count === 0 ? FlausenStyle.card : "transparent"
            list.spacing: 8

            model: ScriptModel {
                values: [...Audio.appStreams]
            }

            delegate: AppStreamRow {
                id: stream

                required property PwNode modelData
                required property int index

                anchors.left: streamList.list.contentItem.left
                anchors.right: streamList.list.contentItem.right
                first: index === 0
                last: index === streamList.list.count - 1

                node: stream.modelData
            }
        }
    }
}
