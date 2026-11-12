import QtQuick
import qs.services

// Only a transparent tint. The compositor blurs the actual windows behind us.
Rectangle {
    property bool rounded: true
    property bool smoke: false
    radius: rounded ? height / 2 : 0
    color: smoke ? MenuStyle.taskbarSurface : Colours.light ? "#59f8f6f3" : "#401c2024"
    border.width: 1
    border.color: smoke ? MenuStyle.border : Colours.light ? "#66ffffff" : "#38ffffff"
}
