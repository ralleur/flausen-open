pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import qs.components
import qs.modules.nexus
import qs.modules.nexus.common
import "../flausen"
PageBase {
    id: root
    readonly property var sections: ({
        17: {title:qsTranslate("Flausen", "General"), subtitle:qsTranslate("Flausen", "Your account and everyday essentials."), rows:[
            {title:qsTranslate("Flausen", "User account"), description:qsTranslate("Flausen", "Profile picture, account name and password"), icon:"account_circle", module:"kcm_users"},
            {title:qsTranslate("Flausen", "Language & region"), description:qsTranslate("Flausen", "Language, formats and units"), icon:"language", module:"kcm_regionandlang"},
            {title:qsTranslate("Flausen", "Date & time"), description:qsTranslate("Flausen", "Time zone and automatic time synchronization"), icon:"schedule", module:"kcm_clock"},
            {title:qsTranslate("Flausen", "Default apps"), description:qsTranslate("Flausen", "Browser, email and file manager"), icon:"apps", module:"kcm_componentchooser"},
            {title:qsTranslate("Flausen", "Accessibility"), description:qsTranslate("Flausen", "Support for vision, hearing and interaction"), icon:"accessibility_new", module:"kcm_access"}
        ]},
        18: {title:qsTranslate("Flausen", "Display"), subtitle:qsTranslate("Flausen", "Everything in its place. On every display."), rows:[
            {title:qsTranslate("Flausen", "Display configuration"), description:qsTranslate("Flausen", "Resolution, scaling, arrangement and refresh rate"), icon:"monitor", module:"kcm_kscreen"},
            {title:qsTranslate("Flausen", "Night light"), description:qsTranslate("Flausen", "Warmer screen colors in the evening"), icon:"nightlight", module:"kcm_nightlight"},
            {title:qsTranslate("Flausen", "Power & sleep"), description:qsTranslate("Flausen", "Display timeout and power saving"), icon:"power_settings_new", module:"kcm_powerdevilprofilesconfig"}
        ]},
        19: {title:qsTranslate("Flausen", "Keyboard & mouse"), subtitle:qsTranslate("Flausen", "The way you like to work."), rows:[
            {title:qsTranslate("Flausen", "Keyboard"), description:qsTranslate("Flausen", "Layout, key repeat and Num Lock"), icon:"keyboard", module:"kcm_keyboard"},
            {title:qsTranslate("Flausen", "Mouse"), description:qsTranslate("Flausen", "Speed, acceleration and buttons"), icon:"mouse", module:"kcm_mouse"},
            {title:"Touchpad", description:qsTranslate("Flausen", "Tapping, scrolling and pointer speed"), icon:"touchpad_mouse", module:"kcm_touchpad"},
            {title:qsTranslate("Flausen", "System shortcuts"), description:qsTranslate("Flausen", "Window actions and global KDE shortcuts"), icon:"keyboard_keys", module:"kcm_keys"},
            {title:qsTranslate("Flausen", "Desktop shortcuts"), description:qsTranslate("Flausen", "Caelestia menus and actions"), icon:"keyboard_command_key", page:9}
        ]},
        20: {title:qsTranslate("Flausen", "Privacy & security"), subtitle:qsTranslate("Flausen", "Your access. Your control."), rows:[
            {title:qsTranslate("Flausen", "Screen locking"), description:qsTranslate("Flausen", "Automatic locking and unlocking"), icon:"lock", module:"kcm_screenlocker"},
            {title:qsTranslate("Flausen", "Password & account"), description:qsTranslate("Flausen", "Credentials for your local account"), icon:"key", module:"kcm_users"},
            {title:"Firewall", description:qsTranslate("Flausen", "Network rules and protection for incoming connections"), icon:"shield", module:"kcm_firewall"},
            {title:qsTranslate("Flausen", "Customize lock screen"), description:qsTranslate("Flausen", "Wallpaper and appearance"), icon:"wallpaper", page:0, sub:9}
        ]},
        21: {title:qsTranslate("Flausen", "System"), subtitle:qsTranslate("Flausen", "Your flausen desktop. Everything that matters in one place."), rows:[
            {title:qsTranslate("Flausen", "Updates"), description:qsTranslate("Flausen", "System packages and desktop updates"), icon:"system_update", page:13},
            {title:qsTranslate("Flausen", "System information"), description:qsTranslate("Flausen", "Operating system, hardware and software versions"), icon:"info", module:"kcm_about-distro"},
            {title:qsTranslate("Flausen", "Power management"), description:qsTranslate("Flausen", "Performance profile, battery and sleep"), icon:"battery_full", module:"kcm_powerdevilprofilesconfig"},
            {title:qsTranslate("Flausen", "Session & startup"), description:qsTranslate("Flausen", "Desktop startup behavior"), icon:"login", page:8},
            {title:qsTranslate("Flausen", "Extensions"), description:qsTranslate("Flausen", "Manage installed Caelestia plugins"), icon:"extension", page:14},
            {title:qsTranslate("Flausen", "All system settings"), description:qsTranslate("Flausen", "More devices, services and system options"), icon:"settings", module:""}
        ]}
    })
    readonly property var section: sections[nState.currentPageIdx] ?? sections[17]
    title: section.title
    ColumnLayout {
        anchors {left: parent.left; right: parent.right; top: parent.top}
        spacing: 14
        Text { text: root.section.subtitle; color: FlausenStyle.secondary; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 15} wrapMode: Text.WordWrap; Layout.fillWidth:true; Layout.bottomMargin: 14 }
        Repeater {
            model: root.section.rows
            Button {
                id: row
                required property var modelData
                text: modelData.title
                Layout.fillWidth: true
                implicitHeight: Math.max(80, labels.implicitHeight + 30)
                leftPadding: 18
                rightPadding: 18
                topPadding: 15
                bottomPadding: 15
                Accessible.name: modelData.title + ". " + modelData.description
                onClicked: {
                    if (modelData.page !== undefined) root.nState.goToSubPage(modelData.page, modelData.sub ?? -1);
                    else root.nState.openSystemModule(modelData.module || "@catalogue", modelData.title);
                }
                background: Rectangle { radius: 14; color: row.hovered ? FlausenStyle.selected : FlausenStyle.card; border {width: row.visualFocus ? 2 : 1; color: row.visualFocus ? FlausenStyle.accent : FlausenStyle.line} }
                contentItem: RowLayout {
                    spacing: 16
                    SettingsIcon { name: row.modelData.icon; Layout.alignment: Qt.AlignVCenter; Layout.preferredWidth: 48; Layout.preferredHeight: 48 }
                    ColumnLayout {
                        id: labels
                        Layout.fillWidth: true
                        spacing: 5
                        Text {text:row.modelData.title; color:FlausenStyle.text; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 15; weight:Font.Medium} Layout.fillWidth:true; wrapMode:Text.WordWrap}
                        Text {text:row.modelData.description; color:FlausenStyle.secondary; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 12} Layout.fillWidth:true; wrapMode:Text.WordWrap}
                    }
                    SettingsIcon {name:"chevron_right"; color:FlausenStyle.secondary; fieldSize:24; glyphPixels:24; Layout.alignment:Qt.AlignVCenter; Layout.preferredWidth:24; Layout.preferredHeight:24}
                }
            }
        }
        Text { text:qsTranslate("Flausen", "flausen. · Your desktop on KDE & Caelestia"); color:FlausenStyle.secondary; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 12} Layout.topMargin:16; Layout.fillWidth:true; wrapMode:Text.WordWrap }
    }
}
