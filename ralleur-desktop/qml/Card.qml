import QtQuick

Rectangle {
    radius: Theme.geo.cardRadius
    color: Qt.alpha(Theme.colors.surface, Theme.tokens.effects?.surfaceOpacity ?? 0.94)
    border.color: Theme.colors.stroke
    border.width: 1
}
