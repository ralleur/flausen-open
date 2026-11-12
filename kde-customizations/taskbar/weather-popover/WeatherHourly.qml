pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services
import qs.utils

Rectangle {
    id: root
    required property var entries
    property real geometryScale: 1
    property real textPixels: 16
    property int offset: 0
    property int windowSize: 7
    readonly property var page: entries.slice(offset,offset+windowSize)
    readonly property real cellWidth: (width-24*geometryScale)/windowSize
    readonly property real minTemp: page.length ? Math.min(...page.map(e=>Number(e.tempC))) : 0
    readonly property real maxTemp: page.length ? Math.max(...page.map(e=>Number(e.tempC))) : 0
    readonly property bool showRain: page.some(e=>(e.precipChance ?? 0)>=20)
    implicitHeight: (210+(showRain?22:0))*geometryScale
    color: MenuStyle.cardFill
    radius: 17*geometryScale
    border.width: 1
    border.color: MenuStyle.rule
    function pointX(i) {return 12*geometryScale+cellWidth*(i+0.5);}
    function pointY(temp) {
        const range=Math.max(5,maxTemp-minTemp);
        return 42*geometryScale+(maxTemp-temp)/range*68*geometryScale;
    }
    function label(entry) {
        if(entry.isCurrent) return qsTr("Now");
        const date=new Date(entry.timestamp);
        if(!isNaN(date.getTime())) return Qt.formatDateTime(date,Units.twelveHourClock?"h AP":"HH:mm");
        return String(entry.hour).padStart(2,"0")+":00";
    }
    onPageChanged: curve.requestPaint()
    onMinTempChanged: curve.requestPaint()
    onMaxTempChanged: curve.requestPaint()
    Canvas {
        id: curve
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const c=getContext("2d");c.reset();if(!root.page.length)return;
            const pts=root.page.map((e,i)=>({x:root.pointX(i),y:root.pointY(e.tempC)}));
            function path() {
                c.beginPath();c.moveTo(pts[0].x,pts[0].y);
                for(let i=1;i<pts.length;i++) {const a=pts[i-1],b=pts[i],mid=(a.x+b.x)/2;c.bezierCurveTo(mid,a.y,mid,b.y,b.x,b.y);}
            }
            path();c.lineTo(pts[pts.length-1].x,140*root.geometryScale);c.lineTo(pts[0].x,140*root.geometryScale);c.closePath();
            const gradient=c.createLinearGradient(0,28*root.geometryScale,0,140*root.geometryScale);
            gradient.addColorStop(0,Qt.alpha(MenuStyle.accent,.30));gradient.addColorStop(1,Qt.alpha(MenuStyle.accent,0));c.fillStyle=gradient;c.fill();
            path();c.strokeStyle=MenuStyle.accent;c.lineWidth=2.4*root.geometryScale;c.stroke();
            for(const p of pts){c.beginPath();c.arc(p.x,p.y,4.6*root.geometryScale,0,Math.PI*2);c.fillStyle=MenuStyle.accent;c.fill();}
        }
    }
    Repeater {
        model: root.page
        Item {
            id: cell
            required property var modelData
            required property int index
            x: root.pointX(index)-width/2
            width: root.cellWidth
            height: root.height
            MenuText {
                anchors.horizontalCenter: parent.horizontalCenter
                y: root.pointY(cell.modelData.tempC)-height-9*root.geometryScale
                text: Weather.formatTemp(cell.modelData.tempC,true)
                font.pixelSize: root.textPixels
            }
            MenuText {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 142*root.geometryScale
                text: root.label(cell.modelData)
                font.pixelSize: root.textPixels*.82
                color: cell.modelData.isCurrent ? "#91c8e8" : MenuStyle.muted
            }
            WeatherSymbol {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 168*root.geometryScale
                width: 38*root.geometryScale;height:width
                condition: cell.modelData.icon || "cloud"
            }
            MenuText {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 207*root.geometryScale
                visible: root.showRain && (cell.modelData.precipChance ?? 0)>=20
                text: (cell.modelData.precipChance ?? 0)+"%"
                font.pixelSize: root.textPixels*.75
                color: "#91c8e8"
            }
        }
    }
}
