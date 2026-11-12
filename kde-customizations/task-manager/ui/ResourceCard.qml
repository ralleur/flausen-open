import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import qs.modules.nexus.flausen
Rectangle {
    id: card
    required property var cardData
    property var graphClock: null
    property var translate: function(text){return text;}
    radius: 14; color: FlausenStyle.card; border.color: FlausenStyle.line
    implicitHeight: 146
    HoverHandler { id: cardHover }
    C.ToolTip.visible: cardHover.hovered
    C.ToolTip.delay: 500
    C.ToolTip.text: card.cardData.name+'\n'+(card.cardData.device??'')+(card.cardData.path?'\n'+card.cardData.path:'')
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 4
        TMText { text: card.cardData.name; size: 15; color: FlausenStyle.text; Layout.fillWidth: true }
        TMText { visible:text.length>0; text: card.cardData.device??''; size: 12; color: FlausenStyle.secondary; Layout.fillWidth: true }
        TMText { text: card.cardData.value; size: card.cardData.kind === 'memory' ? 21 : 25; color: FlausenStyle.text; Layout.fillWidth: true }
        Item {
            Layout.fillWidth: true; Layout.fillHeight: true; implicitHeight: 22
            Row {
                visible: card.cardData.kind !== 'network'; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; spacing: 2
                Repeater {
                    model: 20
                    Rectangle { required property int index; width: Math.max(3,(card.width*.55-38)/20); height: 13; radius: 1; color: card.cardData.percent !== null && index < card.cardData.percent/5 ? card.cardData.color : Qt.alpha(FlausenStyle.secondary,.26) }
                }
            }
            Sparkline { graphClock:card.graphClock;seriesId:card.cardData.id;anchors.right: parent.right; width: card.cardData.kind === 'network' ? parent.width : parent.width*.34; height: parent.height; values: card.cardData.history; ink: card.cardData.color; ceiling: card.cardData.kind === 'network' ? 0 : 100 }
        }
        TMText { text: card.cardData.detail; size: 12; color: FlausenStyle.secondary; Layout.fillWidth: true }
    }
}
