import QtQuick
import org.kde.plasma.core as PlasmaCore

PlasmaCore.Dialog {
    id: preview
    objectName: "ralleur-drop-indicator"
    type: PlasmaCore.Dialog.OnScreenDisplay
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus
    location: PlasmaCore.Types.Floating
    backgroundHints: PlasmaCore.Dialog.NoBackground
    outputOnly: true
    hideOnWindowDeactivate: false
    visible: false
    property var area: ({x:0,y:0,width:0,height:0})
    property var rectangles: []
    property int selected: -1
    property string actionLabel: ""
    property var targetGeometry: selected >= 0 ? rectangles[selected] : null
    property bool indicatorReady: false
    function showPlan(a, rects, index, label) {
        area = a; rectangles = rects; selected = index; actionLabel = label
        x = area.x; y = area.y
        if (!visible) {
            indicatorReady = false
            visible = true
            settle.restart()
        }
    }
    function hide() { settle.stop(); indicatorReady = false; visible = false }
    property Timer settleTimer: Timer {
        id: settle
        interval: 0
        onTriggered: { preview.x = preview.area.x; preview.y = preview.area.y; preview.indicatorReady = true }
    }
    mainItem: Item {
        width: preview.area.width
        height: preview.area.height
        visible: preview.indicatorReady
        Repeater {
            model: preview.rectangles
            Rectangle {
                required property var modelData
                required property int index
                x: modelData.x - preview.area.x
                y: modelData.y - preview.area.y
                width: modelData.width
                height: modelData.height
                radius: 12
                color: index === preview.selected ? "#333dabcc" : "#08000000"
                border.width: index === preview.selected ? 3 : 1
                border.color: index === preview.selected ? "#83d4ef" : "#45ffffff"
            }
        }
        Rectangle {
            x: preview.targetGeometry ? preview.targetGeometry.x - preview.area.x + 16 : (parent.width-width)/2
            y: preview.targetGeometry ? preview.targetGeometry.y - preview.area.y + 16 : 80
            width: label.implicitWidth + 28
            height: label.implicitHeight + 18
            radius: 10
            color: "#ed18242c"
            border.color: "#83d4ef"
            Text {
                id: label
                anchors.centerIn: parent
                text: preview.actionLabel
                font.pixelSize: 16
                font.weight: Font.DemiBold
                color: "#eafaff"
            }
        }
    }
}
