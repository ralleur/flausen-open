import QtQuick
import Caelestia.Components

// Same antialiased native renderer and linear slide used by the network popout.
Item {
    id: chart
    property var values: []
    property color ink: '#479cff'
    property real ceiling: 100
    property bool fill: true
    property var graphClock: null
    property string seriesId: ''
    readonly property var series: graphClock ? (graphClock.streams[seriesId]??null) : fallback
    readonly property real slideProgress: graphClock?.slideProgress??1
    readonly property int sampleCount: series?.buffer.count??0
    clip: true
    GraphSeries { id: fallback }
    onValuesChanged: { if(!graphClock)fallback.replace(values); }
    Component.onCompleted: { if(!graphClock)fallback.replace(values); }
    SparklineItem {
        id: nativeGraph
        anchors.fill: parent
        anchors.topMargin: 2; anchors.bottomMargin: 3
        line1: chart.series?.buffer??null
        line1Color: chart.ink
        line1FillAlpha: chart.fill ? 0.15 : 0
        lineWidth: 1.5
        historyLength: 60
        maxValue: chart.ceiling>0 ? chart.ceiling : Math.max(1,chart.series?.smoothMaximum??1)
        slideProgress: chart.slideProgress
    }
}
