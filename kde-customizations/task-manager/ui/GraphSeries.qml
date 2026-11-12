import QtQuick
import Caelestia
import Caelestia.Config

// Kept by GraphClock, independently of the periodically rebuilt view delegates.
Item {
    id: series
    visible: false
    property alias buffer: samples
    property bool initialized: false
    property real targetMaximum: 1
    property real smoothMaximum: targetMaximum
    CircularBuffer { id: samples; capacity: 60 }
    Behavior on smoothMaximum {
        enabled: series.initialized && GlobalConfig.appearance.anim.enabled
        NumberAnimation { duration: 180; easing.type: Easing.InOutCubic }
    }
    function replace(values) {
        samples.clear();
        for(const value of values??[])
            if(value!==null && Number.isFinite(value))samples.push(value);
        targetMaximum=Math.max(1,samples.maximum*1.2);
        initialized=true;
    }
}
