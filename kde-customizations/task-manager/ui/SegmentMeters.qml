pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import qs.modules.nexus.flausen

Item {
    id: meters
    property var units: []
    property color ink: '#479cff'
    property bool historyMode: true
    property var translate: function(text){return text;}
    property var graphClock: null
    property string seriesId: ''
    readonly property int minimumCellWidth: 64
    readonly property real cellWidth: Math.max(0,(width-Math.max(0,columns-1)*8)/columns)
    readonly property int columns: Math.max(1, Math.min(units.length, Math.floor((width+8)/(minimumCellWidth+8))))
    readonly property int rows: Math.ceil(units.length/columns)
    implicitHeight: rows*112+Math.max(0,rows-1)*8
    Grid {
        width: meters.width
        columns: meters.columns
        spacing: 8
        Repeater {
            model: meters.units
            Item {
                id: cell
                required property var modelData
                width: meters.cellWidth; height: 112
                Accessible.name: modelData.name+', '+Math.round(modelData.value)+' '+meters.translate('Percent')+'. '+modelData.detail
                HoverHandler { id: hover }
                C.ToolTip.visible: hover.hovered
                C.ToolTip.delay: 400
                C.ToolTip.text: cell.modelData.name+' · '+cell.modelData.detail
                TMText { y:5; width:cell.width; text:cell.modelData.name;size:11;color:FlausenStyle.secondary;horizontalAlignment:Text.AlignHCenter }
                Column {
                    visible: !meters.historyMode
                    y:25
                    width:cell.width;spacing:2
                    Repeater {
                        model:16
                        Rectangle {
                            required property int index
                            width:cell.width;height:2;radius:1
                            color:15-index<Math.ceil(Math.max(0,Math.min(100,cell.modelData.value))/100*16) ? meters.ink : Qt.alpha(FlausenStyle.secondary,.2)
                        }
                    }
                }
                Sparkline { graphClock:meters.graphClock;seriesId:'unit:'+meters.seriesId+':'+cell.modelData.id;visible:meters.historyMode;x:0;y:25;width:cell.width;height:62;values:cell.modelData.history??[];ink:meters.ink;ceiling:100 }
                TMText { y:90;width:cell.width;text:Math.round(cell.modelData.value)+'%';size:12;color:FlausenStyle.text;horizontalAlignment:Text.AlignHCenter }
            }
        }
    }
}
