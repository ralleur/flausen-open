pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Templates as T
import org.kde.kirigami as Kirigami
import qs.components
import qs.components.controls
import qs.services
Item {
    id: root
    required property Item targetItem
    // Keep page-back navigation idempotent within the current module.
    property string moduleKey: ""
    property var processed: []
    onModuleKeyChanged: processed=[]
    function plainLabel(text): string {
        return String(text).replace(/&&/g, "\u0001").replace(/&(?=.)/g, "").replace(/\u0001/g, "&");
    }
    function apply(item): void {
        if (!item) return;
        if (item instanceof FlausenButton || item instanceof FlausenSwitch || item instanceof FlausenSlider) return;
        if (processed.indexOf(item) < 0) {
            processed.push(item);
            // FormEntry's native minimum omits trailing controls. Keep room for
            // contextual help, including rows with a slider and a numeric input.
            if ((item.trailingItems?.length ?? 0)>0 && item.fullWidth !== undefined && item.contentItem)
                formEntryAdapter.createObject(item,{entry:item,nativeMinimum:item.implicitWidth});
            // Preserve content, models, validation and every native signal handler.
            if (item instanceof T.Control) {
                const bold = item.font.bold;
                item.font = Qt.binding(() => Qt.font({family:FlausenStyle.family, pixelSize:14*FlausenStyle.fontScale, bold:bold}));
            }
            if ((item instanceof T.Pane && !(item instanceof T.Page) && !(item instanceof T.ScrollView)) || item instanceof T.Frame || item instanceof T.GroupBox || item.showClickFeedback !== undefined) {
                item.background=panelBackground.createObject(item,{control:item});
            }
            // KScreen's rotation buttons size themselves from childrenRect. A
            // replacement background must not feed that height binding back.
            if (item instanceof T.ToolButton && typeof item.outputRotation === "number") item.height=Math.max(32,item.implicitHeight);
            if (item instanceof T.AbstractButton) labelAdapter.createObject(item,{control:item});
            if (item instanceof T.Switch) item.indicator = switchIndicator.createObject(item,{control:item});
            else if (item instanceof T.CheckBox) item.indicator = checkIndicator.createObject(item,{control:item});
            else if (item instanceof T.RadioButton) item.indicator = checkIndicator.createObject(item,{control:item,radio:true});
            else if (item instanceof T.Button || item instanceof T.ToolButton || item instanceof T.ComboBox || item instanceof T.SpinBox || item instanceof T.TextField || item instanceof T.TextArea) {
                const nativeBackground=item.background;
                item.background = controlBackground.createObject(item,{
                    control:item, field:item instanceof T.TextField || item instanceof T.TextArea,
                    nativeWidth:nativeBackground?.implicitWidth ?? 0,
                    nativeHeight:nativeBackground?.implicitHeight ?? 0
                });
            } else if (item instanceof T.Slider) {
                item.background = sliderTrack.createObject(item,{control:item});
                item.handle = sliderHandle.createObject(item,{control:item});
            }
        }
        for (const child of item.children ?? []) {
            // A ComboBox owns a private TextField even in non-editable mode.
            // Styling it as another public field creates nested/double borders.
            if(item instanceof T.ComboBox && child===item.contentItem)continue;
            apply(child);
        }
    }
    onTargetItemChanged: Qt.callLater(() => apply(targetItem))
    Timer { interval:350; repeat:true; running:root.visible && root.targetItem !== null; triggeredOnStart:true; onTriggered:root.apply(root.targetItem) }
    Component {
        id: formEntryAdapter
        QtObject {
            id: sizing
            required property var entry
            required property real nativeMinimum
            function extraWidth(items): real {
                let total=0;
                for(const item of items ?? [])if(item.visible)
                    total+=Math.max(0,item.implicitWidth)+Kirigami.Units.smallSpacing;
                return total;
            }
            Component.onCompleted: entry.implicitWidth=Qt.binding(() => Math.max(
                sizing.nativeMinimum,
                (sizing.entry.contentItem?.implicitWidth ?? 0)+Kirigami.Units.largeSpacing*2
                    +sizing.extraWidth(sizing.entry.leadingItems)+sizing.extraWidth(sizing.entry.trailingItems)));
        }
    }
    Component {
        id: labelAdapter
        QtObject {
            id: adapter
            required property var control
            readonly property Item label: control?.contentItem ?? null
            function refresh(): void {
                if(label && typeof label.text === "string")
                    label.text=Qt.binding(() => root.plainLabel(adapter.control.text));
            }
            onLabelChanged: Qt.callLater(refresh)
            Component.onCompleted: refresh()
        }
    }
    Component {
        id: panelBackground
        Rectangle {property var control; color:control?.checked || (control?.showClickFeedback && (control?.hovered || control?.down)) ? FlausenStyle.selected : FlausenStyle.card;radius:14;border.width:1;border.color:FlausenStyle.line}
    }
    Component {
        id: controlBackground
        Rectangle {
            required property var control
            property bool field: false
            property real nativeWidth: 0
            property real nativeHeight: 0
            implicitWidth: nativeWidth
            implicitHeight: nativeHeight
            radius: field ? 9 : 12
            color: field ? FlausenStyle.card : control.checked || control.down || control.hovered ? FlausenStyle.selected : FlausenStyle.card
            border.width: control.activeFocus ? 2 : 1
            border.color: control.activeFocus || control.checked ? FlausenStyle.accent : FlausenStyle.line
            opacity: control.enabled ? 1 : 0.45
        }
    }
    Component {
        id: switchIndicator
        Rectangle {
            required property var control
            implicitWidth:44; implicitHeight:25
            x: control.text ? (control.mirrored ? control.width-width-control.rightPadding : control.leftPadding) : (control.width-width)/2; y: control.topPadding+(control.availableHeight-height)/2
            radius:13
            color:control.checked ? FlausenStyle.accent : FlausenStyle.light ? "#d2d3d6" : "#464b52"
            PrimaryControlFill {} // Capture primary material
            opacity:control.enabled ? 1 : .4
            Rectangle {x:parent.control.checked ? 22 : 3; y:3; width:19; height:19; radius:10; color:"white"; Behavior on x {NumberAnimation {duration:FlausenStyle.motionDuration}}}
        }
    }
    Component {
        id: checkIndicator
        Rectangle {
            required property var control
            property bool radio: false
            implicitWidth:20; implicitHeight:20
            x: control.text ? (control.mirrored ? control.width-width-control.rightPadding : control.leftPadding) : (control.width-width)/2; y:control.topPadding+(control.availableHeight-height)/2
            radius:radio ? 10 : 6
            color:control.checked && !radio ? FlausenStyle.accent : FlausenStyle.card
            PrimaryControlFill {} // Capture primary material
            border.width:control.activeFocus ? 2 : 1
            border.color:control.checked || control.activeFocus ? FlausenStyle.accent : FlausenStyle.secondary
            opacity:control.enabled ? 1 : .4
            Text {anchors.centerIn:parent;visible:parent.control.checked && !parent.radio;text:parent.control.checkState === Qt.PartiallyChecked ? "−" : "✓";color:"white";font.pixelSize:15}
            Rectangle {anchors.centerIn:parent;visible:parent.control.checked && parent.radio;width:10;height:10;radius:5;color:FlausenStyle.accent; PrimaryControlFill {} }
        }
    }
    Component {
        id: sliderTrack
        SegmentedTrack {
            fillColor: Colours.palette.m3primary
            emptyColor: FlausenStyle.light ? "#c2c5c9" : "#575b60"
            outlineColor: FlausenStyle.light ? "#333b45" : "#e2e5e8"
        }
    }
    Component {
        id: sliderHandle
        SegmentedHandle {}
    }
}
