pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Effects
import QtQuick.Layouts
import Quickshell
import Quickshell.Widgets
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.components.effects
import qs.services
import qs.modules.drawers

MouseArea {
    id: root

    enum Side {
        Top,
        Bottom,
        Left,
        Right
    }

    required property Item attachTo
    property int attachSideX: Menu.Right
    property int attachSideY: Menu.Bottom
    property int thisSideX: Menu.Right
    property int thisSideY: Menu.Top
    property bool constrainToWindow: false
    property real marginX
    property real marginY

    property list<MenuItem> items
    property var dynamicModel: items
    property MenuItem active: dynamicModel[0] ?? null
    property bool expanded
    property bool rightClickReposition: false
    property real maxHeight: 320
    readonly property alias backgroundItem: menu
    property bool dolphinContextStyle: false
    property bool sharedPopoverStyle:false
    property real menuFontScale:1.15
    property real menuGeometryScale:1.15
    readonly property bool styledMenu:dolphinContextStyle || sharedPopoverStyle
    property bool transparentBackground: false
    // Unfold sideways from the anchor with a short, non-overshooting curve
    // instead of dropping down.
    property bool revealHorizontal: false
    readonly property int firstVisibleIndex: {
        const model = dynamicModel ?? [];
        for (let i = 0; i < model.length; i++)
            if (model[i]?.visible)
                return i;
        return -1;
    }
    readonly property int lastVisibleIndex: {
        const model = dynamicModel ?? [];
        for (let i = model.length - 1; i >= 0; i--)
            if (model[i]?.visible)
                return i;
        return -1;
    }

    signal itemSelected(item: MenuItem)
    signal rightClickedAt(real x, real y)

    // Plays the opening animation again, e.g. after the menu moved while open.
    function replayReveal(): void {
        if (!revealHorizontal || !expanded)
            return;
        revealOut.stop();
        revealIn.stop();
        menu.hScale = 0;
        revealIn.start();
    }

    onExpandedChanged: {
        if (!revealHorizontal)
            return;
        revealIn.stop();
        revealOut.stop();
        if (expanded)
            revealIn.start();
        else
            revealOut.start();
    }

    parent: {
        let node = root.attachTo;
        let interactionsNode = null;

        while (node && node.parent) {
            if (node.utilitiesShortcutActive !== undefined) {
                interactionsNode = node;
            }
            node = node.parent;
        }

        if (interactionsNode) {
            return interactionsNode;
        }

        return node || root.parent;
    }
    anchors.fill: parent

    enabled: expanded
    acceptedButtons: rightClickReposition ? Qt.LeftButton | Qt.RightButton : Qt.LeftButton
    onClicked: mouse => {
        if (rightClickReposition && mouse.button === Qt.RightButton) {
            rightClickedAt(mouse.x, mouse.y);
            return;
        }
        expanded = false;
    }

    opacity: expanded ? 1 : 0
    visible: opacity > 0

    Behavior on opacity {
        Anim {
            type: root.revealHorizontal ? Anim.FastEffects : Anim.DefaultEffects
        }
    }

    NumberAnimation {
        id: revealIn

        target: menu
        property: "hScale"
        to: 1
        duration: Tokens.anim.durations.small
        easing: Tokens.anim.emphasizedDecel
    }

    NumberAnimation {
        id: revealOut

        target: menu
        property: "hScale"
        to: 0
        duration: Math.round(Tokens.anim.durations.small * 0.75)
        easing: Tokens.anim.emphasizedAccel
    }

    // Native smoke for taskbar dropdowns only.
    TaskbarDropdownGlass {
        screen: root.QsWindow.window?.screen ?? Quickshell.screens[0]
        active: root.sharedPopoverStyle && root.expanded && root.visible
        geometry: Qt.rect(menu.x, menu.y, menu.width, menu.height)
        reserveGeometry: Qt.rect(menu.x, menu.y, menu.implicitWidth, menu.implicitHeight)
        bottomAnchored: root.thisSideY === Menu.Bottom
        cornerRadius: menu.radius
    }

    TransformWatcher {
        id: watcher

        a: root.parent
        b: root.attachTo
    }

    Elevation {
        id: menu

        property string vAnchor: "none"
        property string hAnchor: "none"
        property real offsetScale: 1 - animScale
        property real vScale: root.expanded ? 1 : 0.0
        property real hScale: 0
        readonly property real animScale: root.revealHorizontal ? hScale : vScale

        x: {
            watcher.transform;
            const item = root.attachTo;
            if (!item || !root.parent)
                return 0;
            let off = root.attachSideX === Menu.Left ? 0 : item.width;
            if (root.thisSideX === Menu.Right)
                off -= width;
            const pt = item.mapToItem(root.parent, off, 0);
            const desired = (pt ? pt.x : 0) + root.marginX;
            return root.constrainToWindow ? Math.max(8, Math.min(root.parent.width - width - 8, desired)) : desired;
        }
        y: {
            watcher.transform;
            const item = root.attachTo;
            if (!item || !root.parent)
                return 0;
            let off = root.attachSideY === Menu.Top ? 0 : item.height;
            if (root.thisSideY === Menu.Bottom)
                off -= height;
            const pt = item.mapToItem(root.parent, 0, off);
            return (pt ? pt.y : 0) + root.marginY;
        }

        radius: root.styledMenu ? MenuStyle.contextRadius : Tokens.rounding.large
        level: root.transparentBackground ? 0 : 2
        implicitWidth: Math.max(200, column.implicitWidth + (root.styledMenu ? MenuStyle.contextPadding : Tokens.padding.extraSmall) * 2)
        implicitHeight: Math.min(root.maxHeight, column.implicitHeight + (root.styledMenu ? MenuStyle.contextPadding : Tokens.padding.extraSmall) * 2)
        width: root.revealHorizontal ? implicitWidth * animScale : implicitWidth
        height: root.revealHorizontal ? implicitHeight : implicitHeight * animScale
        clip: root.revealHorizontal

        Behavior on vScale {
            enabled: !root.revealHorizontal

            Anim {}
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onWheel: e => e.accepted = true
            onClicked: {}
        }

        // The dropdown shares a window with its parent popover. Blur that QML
        // content separately; compositor blur only sees the desktop below both.
        ShaderEffectSource {
            id: taskbarDropdownSource
            sourceItem: root.sharedPopoverStyle ? (root.parent?.panels?.popoutsWrapper ?? null) : null
            sourceRect: {
                void menu.x; void menu.y; void menu.width; void menu.height;
                if (!sourceItem) return Qt.rect(0, 0, 0, 0);
                const pos = menu.mapToItem(sourceItem, 0, 0);
                return Qt.rect(pos.x, pos.y, menu.width, menu.height);
            }
            textureSize: Qt.size(Math.max(1, menu.width), Math.max(1, menu.height))
            live: root.expanded
            hideSource: false
            visible: false
        }
        MultiEffect {
            visible: root.sharedPopoverStyle && root.expanded && taskbarDropdownSource.sourceItem !== null
            width: menu.width; height: menu.height
            source: taskbarDropdownSource
            autoPaddingEnabled: false
            blurEnabled: true
            blurMax: 48
            blur: 1
            maskEnabled: true
            maskSource: ShaderEffectSource {
                sourceItem: Rectangle {
                    width: menu.width; height: menu.height
                    radius: menu.radius
                    color: "white"
                }
                hideSource: true
            }
        }

        StyledRect {
            // Sideways, the content stays pinned to the edge the menu grows
            // from and trails it by a few pixels while the panel unfolds.
            x: {
                if (!root.revealHorizontal)
                    return 0;
                const trail = (1 - menu.animScale) * Tokens.padding.extraLarge;
                return root.thisSideX === Menu.Right ? menu.width - menu.implicitWidth + trail : -trail;
            }
            y: root.thisSideY === Menu.Bottom ? menu.height - menu.implicitHeight : 0
            width: menu.implicitWidth
            height: menu.implicitHeight
            opacity: root.revealHorizontal ? Math.min(1, menu.animScale * 1.5) : 1

            transform: Scale {
                yScale: root.revealHorizontal ? 1 : menu.animScale
                origin.y: root.thisSideY === Menu.Bottom ? menu.implicitHeight : 0
            }

            radius: parent.radius
            border.width: root.styledMenu ? 1 : 0
            border.color: root.sharedPopoverStyle ? MenuStyle.border : MenuStyle.contextBorder
            color: root.sharedPopoverStyle ? MenuStyle.taskbarSurface : root.styledMenu ? MenuStyle.contextSurface : root.transparentBackground
                ? Qt.alpha(Colours.palette.m3surfaceContainerLow, 0)
                : (GlobalConfig.appearance.pitchBlack
                    ? "#000000"
                    : Colours.palette.m3surfaceContainerLow)

            Flickable {
                id: flickable

                anchors.fill: parent
                anchors.margins: root.styledMenu ? MenuStyle.contextPadding : Tokens.padding.extraSmall
                contentWidth: width
                contentHeight: column.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                interactive: contentHeight > height

                ScrollBar.vertical: StyledScrollBar {
                    flickable: flickable
                }

                ColumnLayout {
                    id: column

                    width: parent.width
                    spacing: 0

                    Repeater {
                        id: repeater

                        model: root.dynamicModel

                    StyledRect {
                        id: item

                        required property int index
                        required property MenuItem modelData
                        readonly property bool active: modelData === root?.active

                        visible: modelData?.visible ?? false

                        Layout.fillWidth: true
                        implicitWidth: menuOptionRow.implicitWidth + (root.styledMenu ? 36 : Tokens.padding.medium * 2)
                        implicitHeight: visible ? menuOptionRow.implicitHeight + (root.styledMenu ? ((modelData?.footerAction ?? false) ? 16 : 22) : Tokens.padding.medium * 2) : 0
                        Layout.topMargin: root.styledMenu && (modelData?.footerAction ?? false) ? 8 : 0


                        radius: root.styledMenu ? MenuStyle.contextRowRadius : active ? Tokens.rounding.medium : Tokens.rounding.extraSmall
                        topLeftRadius: root.styledMenu ? MenuStyle.contextRowRadius : index === root.firstVisibleIndex ? Tokens.rounding.medium : radius
                        topRightRadius: root.styledMenu ? MenuStyle.contextRowRadius : index === root.firstVisibleIndex ? Tokens.rounding.medium : radius
                        bottomLeftRadius: root.styledMenu ? MenuStyle.contextRowRadius : index === root.lastVisibleIndex ? Tokens.rounding.medium : radius
                        bottomRightRadius: root.styledMenu ? MenuStyle.contextRowRadius : index === root.lastVisibleIndex ? Tokens.rounding.medium : radius

                        color: root.styledMenu && contextMouse.containsMouse ? MenuStyle.contextHover : "transparent"

                        Rectangle {
                            visible:root.styledMenu && (item.modelData?.footerAction ?? false)
                            x:10;y:-4;width:parent.width-20;height:1
                            color:MenuStyle.contextBorder
                        }
                        MouseArea {
                            id:contextMouse
                            anchors.fill:parent
                            visible:root.styledMenu
                            hoverEnabled:true
                            onClicked:{root.itemSelected(item.modelData);root.active=item.modelData;item.modelData.clicked();root.expanded=false;}
                        }

                        Behavior on radius {
                            Anim {}
                        }

                        StateLayer {
                            visible: !root.styledMenu
                            topLeftRadius: parent.topLeftRadius
                            topRightRadius: parent.topRightRadius
                            bottomLeftRadius: parent.bottomLeftRadius
                            bottomRightRadius: parent.bottomRightRadius

                            color: Colours.palette.m3onSurface
                            disabled: !root.expanded
                            onClicked: {
                                root.itemSelected(item.modelData);
                                root.active = item.modelData;
                                item.modelData.clicked();
                                root.expanded = false;
                            }
                        }

                        RowLayout {
                            id: menuOptionRow

                            anchors.fill: parent
                            anchors.leftMargin:root.styledMenu ? 12 : Tokens.padding.medium
                            anchors.rightMargin:root.styledMenu ? 22 : Tokens.padding.medium
                            anchors.topMargin:root.styledMenu ? ((item.modelData?.footerAction ?? false) ? 8 : 11) : Tokens.padding.medium
                            anchors.bottomMargin:root.styledMenu ? ((item.modelData?.footerAction ?? false) ? 8 : 11) : Tokens.padding.medium
                            spacing: Tokens.spacing.small

                            IconImage {
                                visible:root.dolphinContextStyle && !(item.modelData?.footerAction ?? false)
                                Layout.preferredWidth:16;Layout.preferredHeight:16
                                source:Quickshell.iconPath(({skip_next:"media-skip-forward",settings:"settings-configure",content_paste:"edit-paste",terminal:"utilities-terminal",wallpaper:"preferences-desktop-wallpaper",widgets:"preferences-desktop-widgets",sort:"view-sort-ascending",visibility:"view-visible",visibility_off:"view-hidden",lock:"object-locked",lock_open:"object-unlocked"})[item.modelData?.icon] ?? item.modelData?.icon,"application-x-executable")
                            }
                            MaterialIcon {
                                visible:!root.dolphinContextStyle
                                Layout.alignment: Qt.AlignVCenter
                                text: item.modelData?.icon ?? ""
                                color: root.sharedPopoverStyle ? MenuStyle.muted : Colours.palette.m3onSurfaceVariant
                            }

                            StyledText {
                                Layout.alignment: Qt.AlignVCenter
                                Layout.fillWidth: true
                                text: item.modelData?.text ?? ""
                                font:root.styledMenu ? Qt.font({family:MenuStyle.fontFamily,pointSize:(root.sharedPopoverStyle ? MenuStyle.bodyPointSize(root.menuFontScale) : MenuStyle.applicationFont.pointSize)*((item.modelData?.footerAction ?? false) ? 0.85 : 1),italic:(item.modelData?.footerAction ?? false)}) : Tokens.font.body.small
                                color:root.styledMenu ? ((item.modelData?.footerAction ?? false) ? MenuStyle.muted : MenuStyle.ink) : Colours.palette.m3onSurface
                            }

                            StyledText {
                                visible: (item.modelData?.shortcutName?.length ?? 0) > 0
                                text: item.modelData?.shortcutText || qsTr("Not assigned")
                                font:root.sharedPopoverStyle ? Qt.font({family:MenuStyle.fontFamily,pointSize:MenuStyle.bodyPointSize(root.menuFontScale)*0.79}) : Tokens.font.label.medium
                                color: root.sharedPopoverStyle ? MenuStyle.muted : Colours.palette.m3onSurfaceVariant
                            }

                            IconButton {
                                visible: (item.modelData?.shortcutName?.length ?? 0) > 0
                                type: IconButton.Text
                                padding: Tokens.padding.small
                                icon: "edit"
                                font: Tokens.font.icon.small
                                onClicked: item.modelData.editShortcut(this)
                            }

                            Loader {
                                asynchronous: true
                                Layout.alignment: Qt.AlignVCenter
                                active: (item.modelData?.trailingIcon?.length ?? 0) > 0
                                visible: active

                                sourceComponent: MaterialIcon {
                                    text: item.modelData.trailingIcon
                                    color: root.sharedPopoverStyle ? MenuStyle.muted : Colours.palette.m3onSurfaceVariant
                                }
                            }
                        }
                    }
                }
            }
        }
        }
    }
}
