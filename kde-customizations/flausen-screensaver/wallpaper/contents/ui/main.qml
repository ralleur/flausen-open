import QtQuick
import org.kde.plasma.plasmoid
WallpaperItem {
    id: root
    KineticAnimation { anchors.fill: parent; animate: root.visible }
}
