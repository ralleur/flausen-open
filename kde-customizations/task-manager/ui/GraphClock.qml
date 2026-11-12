import QtQuick
import Caelestia.Config

Item {
    id: clock
    visible: false
    property var streams: ({})
    property real interval: 1000
    property real slideProgress: 1
    property int sampleRevision: 0
    property bool initialized: false
    readonly property bool animating: slide.running
    readonly property bool motionEnabled: GlobalConfig.appearance.anim.enabled
    onMotionEnabledChanged: {
        if(!motionEnabled){slide.stop();slideProgress=1;}
    }
    Component { id: seriesFactory; GraphSeries {} }
    NumberAnimation {
        id: slide
        target: clock; property: 'slideProgress'
        to: 1; easing.type: Easing.Linear
    }
    function advance() {
        // Preserve the existing points' position if an extra sample arrives early.
        const start=initialized?slideProgress-1:0;
        slide.stop();
        initialized=true;
        if(!motionEnabled){slideProgress=1;return;}
        slideProgress=start;
        slide.from=start;slide.to=1;slide.duration=Math.max(1,interval);
        slide.start();
    }
    function accept(snapshot) {
        const next={};
        function put(id, values) {
            const series=clock.streams[id]??seriesFactory.createObject(clock);
            series.replace(values);
            next[id]=series;
        }
        for(const card of snapshot.cards){
            put(card.id,card.history);
            for(const unit of card.processors??[])
                put('unit:'+card.id+':'+unit.id,unit.history);
        }
        const detail=snapshot.detail;
        if(detail && !detail.exited){
            const key='process:'+detail.pid+':'+detail.created;
            put(key+':cpu',detail.cpuHistory);
            put(key+':memory',detail.memoryHistory);
        }
        const previous=streams;
        streams=next;
        for(const id of Object.keys(previous))if(!next[id])previous[id].destroy();
        sampleRevision++;
        advance();
    }
}
