import QtQuick
import org.kde.plasma.plasmoid

WallpaperItem {
    id: root
    RalleurAnimation {
        anchors.fill: parent
        animate: root.visible
    }
}
