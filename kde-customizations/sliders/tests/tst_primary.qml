import QtQuick
import QtTest
import qs.components
import qs.services

Item {
    width: 300; height: 160
    Rectangle {
        id: button
        x: 20; y: 20; width: 160; height: 48; radius: 24
        color: "#347fff"
        property bool disabled: false
        property int clicks: 0
        PrimaryControlFill { id: material }
        MouseArea { anchors.fill: parent; onClicked: button.clicks++ }
    }
    TestCase {
        name: "PrimaryControlMaterial"
        when: windowShown
        function cleanup() {
            button.color="#347fff";button.enabled=true;button.disabled=false;
            button.border.width=0;
        }
        function test_blueAndAlternativeAccents() {
            verify(material.visible)
            compare(material.gradient.stops[0].color, MenuStyle.primaryTop)
            compare(material.gradient.stops[1].color, MenuStyle.primaryBottom)
            for (const colour of ["#32b578", "#e83279", "#33ff0000", "#18287dff", "#515962"]) {
                button.color=colour;
                verify(!material.visible,colour)
            }
            button.color="#2862c4";verify(material.visible)
        }
        function test_disabledAndFocusGeometry() {
            button.disabled=true;verify(!material.visible)
            button.disabled=false;button.enabled=false;verify(!material.visible)
            button.enabled=true;button.border.width=2
            compare(material.x,2);compare(material.y,2)
            compare(material.width,button.width-4)
            compare(material.radius,22)
            compare(material.topLeftRadius,22)
        }
        function test_pointerPassesThrough() {
            const before=button.clicks
            mouseClick(button,button.width/2,button.height/2)
            compare(button.clicks,before+1)
        }
    }
}
