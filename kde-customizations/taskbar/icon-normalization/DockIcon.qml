pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io

Item {
    id: root

    property real implicitSize
    readonly property real actualSize: Math.min(width, height)
    readonly property int status: texture.status
    implicitWidth: implicitSize
    implicitHeight: implicitSize

    property url originalSource
    property bool normalize: true
    property url normalizedSource
    property string requestedSource
    readonly property url source: normalizedSource.toString() || originalSource

    // Decode once at native resolution, independently of the display geometry.
    // Mipmaps filter the 512px artwork down to dock size without jagged edges.
    // Changing width/height never changes sourceSize or starts another load.
    Image {
        id: texture
        anchors.fill: parent
        sourceSize: Qt.size(512, 512)
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
        asynchronous: true
        retainWhileLoading: true
        source: root.source
    }

    function request(): void {
        if (!normalize || !originalSource.toString() || normalizer.running)
            return;
        requestedSource = originalSource.toString();
        normalizer.exec([Quickshell.shellPath("scripts/normalize-dock-icon"), requestedSource]);
    }

    onOriginalSourceChanged: {
        normalizedSource = "";
        Qt.callLater(request);
    }
    onNormalizeChanged: {
        normalizedSource = "";
        Qt.callLater(request);
    }
    Component.onCompleted: Qt.callLater(request)

    Process {
        id: normalizer
        environment: ({ QT_QPA_PLATFORM: "offscreen" })
        stdout: StdioCollector {
            onStreamFinished: {
                if (root.normalize && root.requestedSource === root.originalSource.toString()
                        && text.trim().startsWith("file://"))
                    root.normalizedSource = text.trim();
            }
        }
        onExited: {
            if (root.requestedSource !== root.originalSource.toString())
                Qt.callLater(root.request);
        }
    }
}
