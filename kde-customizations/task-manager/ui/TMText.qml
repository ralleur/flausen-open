import QtQuick
import Caelestia.Config
import qs.components
import qs.services
MenuText {
    property real size: MenuStyle.bodyPixels
    font.family: MenuStyle.fontFamily
    font.pixelSize: size * GlobalConfig.appearance.font.scale
    color: MenuStyle.ink
    elide: Text.ElideRight
}
