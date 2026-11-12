pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import QtCore
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils

ColumnLayout {
    id: root
    required property var popouts
    property real scaleOffset: 1
    property real fontScale: 1
    property bool _isSidebarOpen: false
    readonly property real bodyPixels: MenuStyle.bodyPointSize(fontScale)/.75
    property var weather: Weather
    readonly property var allHourly: {
        const future=(weather.hourlyForecast ?? []).filter(e=>e.tempC !== null && e.tempC !== undefined && isFinite(Number(e.tempC))).map(entry=>{
            const solar=root.solarDays[(entry.timestamp ?? "").slice(0,10)];
            const night=solar && (entry.timestamp<solar.rise || entry.timestamp>=solar.set);
            return Object.assign({},entry,{icon:night?(entry.icon ?? "").replace("_day","_night"):entry.icon});
        });
        if (!future.length || !weather.hasWeather) return [];
        return [{isCurrent:true,tempC:weather.tempC,icon:weather.icon,precipChance:0},...future];
    }
    readonly property int windowSize: width<380*scaleOffset?5:7
    readonly property int maxOffset: Math.max(0,allHourly.length-windowSize)
    property int hourOffset: 0
    property bool hourlyExpanded: true
    property bool locationOpen: false
    readonly property bool hoverLocked: locationOpen
    property string observedTime: ""
    property var solarDays: ({})
    onMaxOffsetChanged: hourOffset=Math.min(hourOffset,maxOffset)
    width: Math.min(440*scaleOffset,Math.max(200,((QsWindow.window as QsWindow)?.screen?.width ?? 4096)-80*scaleOffset))
    implicitWidth: width
    spacing: 12*scaleOffset
    Component.onCompleted: weather.reload()

    FileView {
        path: StandardPaths.writableLocation(StandardPaths.CacheLocation)+"/caelestia/weather_cache.json"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: {
            try {
                const data=JSON.parse(text());
                // Observation time from the provider, never the time this menu opened.
                const time=data.current?.time ?? "";
                root.observedTime=time ? time.replace("T"," ") : "";
                const daily=data.daily ?? {}, solar={};
                for(let i=0;i<(daily.time ?? []).length;i++)
                    if(daily.sunrise?.[i] && daily.sunset?.[i]) solar[daily.time[i]]={rise:daily.sunrise[i],set:daily.sunset[i]};
                root.solarDays=solar;
            } catch(e) {root.observedTime="";}
        }
        onLoadFailed: root.observedTime=""
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: 7*root.scaleOffset
        Layout.rightMargin: 7*root.scaleOffset
        Layout.topMargin: 3*root.scaleOffset
        spacing: 10*root.scaleOffset
        WeatherSymbol {
            condition: "location"
            Layout.preferredWidth: 24*root.scaleOffset
            Layout.preferredHeight: 28*root.scaleOffset
        }
        Item {
            Layout.fillWidth: true
            implicitHeight: Math.max(city.implicitHeight,40*root.scaleOffset)
            MenuText {
                id: city
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                width: Math.min(implicitWidth,parent.width-dropdown.implicitWidth-8*root.scaleOffset)
                text: root.weather.city || root.weather.loc || qsTr("Location")
                font.pixelSize: root.bodyPixels*1.65
                elide: Text.ElideRight
            }
            MaterialIcon {
                id: dropdown
                anchors.left: city.right
                anchors.leftMargin: 8*root.scaleOffset
                anchors.verticalCenter: parent.verticalCenter
                text: root.locationOpen ? "expand_less" : "expand_more"
                color: MenuStyle.muted
                fontStyle.pointSize: 18*root.scaleOffset
            }
            StateLayer {
                radius: 10*root.scaleOffset
                color: MenuStyle.ink
                onClicked: {
                    root.locationOpen=!root.locationOpen;
                    if(root.locationOpen) Qt.callLater(()=>locationField.forceActiveFocus());
                }
            }
        }
        WeatherButton {
            objectName: "weatherRefresh"
            icon: "refresh"
            plain: true
            available: !root.weather.loading
            spinning: root.weather.loading
            onClicked: root.weather.refresh()
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        visible: root.locationOpen
        spacing: 8*root.scaleOffset
        StyledTextField {
            id: locationField
            Layout.fillWidth: true
            placeholderText: qsTr("Search location")
            font.family: MenuStyle.fontFamily
            font.pixelSize: root.bodyPixels
            onTextEdited: Weather.queueLocationSearch(text)
            Keys.onEscapePressed: root.locationOpen=false
        }
        MenuText {
            Layout.fillWidth: true
            visible: Weather.locationSearchLoading || Weather.locationSearchError.length>0
            text: Weather.locationSearchLoading ? qsTr("Searching…") : Weather.locationSearchError
            wrapMode: Text.WordWrap
            font.pixelSize: root.bodyPixels*.82
            color: MenuStyle.muted
        }
        Repeater {
            model: Weather.locationSearchResults.slice(0,5)
            TextButton {
                required property var modelData
                Layout.fillWidth: true
                text: modelData.label
                type: ButtonBase.Text
                inactiveOnColour: MenuStyle.ink
                font.family: MenuStyle.fontFamily
                font.pixelSize: root.bodyPixels
                label.width: width-32
                label.elide: Text.ElideRight
                onClicked: {
                    if(Weather.applyLocationResult(modelData)) {
                        root.locationOpen=false;
                        root.hourOffset=0;
                    }
                }
            }
        }
        TextButton {
            text: qsTr("Use automatic location")
            type: ButtonBase.Text
            inactiveOnColour: MenuStyle.muted
            font.family: MenuStyle.fontFamily
            font.pixelSize: root.bodyPixels*.82
            onClicked: { Weather.resetToAutoLocation();root.locationOpen=false;root.hourOffset=0; }
        }
    }

    Rule {}

    RowLayout {
        Layout.alignment: Qt.AlignHCenter
        Layout.fillWidth: true
        Layout.topMargin: 10*root.scaleOffset
        Layout.bottomMargin: 4*root.scaleOffset
        spacing: 22*root.scaleOffset
        Item { Layout.fillWidth: true }
        WeatherSymbol {
            Layout.preferredWidth: Math.min(112*root.scaleOffset,root.width*.26)
            Layout.preferredHeight: Math.min(112*root.scaleOffset,root.width*.26)
            condition: root.weather.icon || "cloud"
        }
        ColumnLayout {
            Layout.maximumWidth: root.width*.52
            spacing: 0
            MenuText {
                text: root.weather.hasWeather ? root.weather.temp : "—"
                font.pixelSize: Math.min(root.bodyPixels*3.6,root.width*.13)
                font.weight: Font.Normal
            }
            MenuText {
                Layout.fillWidth: true
                text: root.weather.hasWeather ? root.weather.description : root.weather.loading ? qsTr("Loading weather…") : qsTr("Weather unavailable")
                font.pixelSize: root.bodyPixels*1.25
                color: MenuStyle.muted
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignLeft
            }
        }
        Item { Layout.fillWidth: true }
    }
    MenuText {
        Layout.fillWidth: true
        Layout.bottomMargin: 8*root.scaleOffset
        text: root.weather.hasWeather ? qsTr("High %1  ·  Low %2").arg(root.weather.maxTemp).arg(root.weather.minTemp) : qsTr("Refresh to try again")
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: root.bodyPixels
        color: MenuStyle.muted
    }

    GridLayout {
        Layout.fillWidth: true
        columns: root.width<360*root.scaleOffset?1:3
        columnSpacing: 6*root.scaleOffset
        rowSpacing: 6*root.scaleOffset
        Metric { icon:"water_drop";label:qsTr("Humidity");value:root.weather.hasWeather?root.weather.humidity+"%":"—";tint:MenuStyle.ink }
        Metric { icon:"thermostat";label:qsTr("Feels like");value:root.weather.hasWeather?root.weather.feelsLike:"—" }
        Metric { icon:"air";label:qsTr("Wind");value:root.weather.hasWeather && isFinite(root.weather.windSpeed)?qsTr("%1 km/h").arg(root.weather.windSpeed):"—" }
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: 3*root.scaleOffset
        spacing: 4*root.scaleOffset
        MenuText {
            Layout.maximumWidth: Math.max(80,root.width-118*root.scaleOffset)
            text: qsTr("Hourly forecast")
            wrapMode: Text.WordWrap
            font.pixelSize: root.bodyPixels*1.2
            font.weight: Font.DemiBold
        }
        WeatherButton {
            objectName: "weatherExpand"
            icon: root.hourlyExpanded?"expand_less":"expand_more"
            plain: true
            onClicked: root.hourlyExpanded=!root.hourlyExpanded
        }
        Item {Layout.fillWidth:true}
        WeatherButton {
            objectName: "weatherPrevious"
            visible: root.hourlyExpanded
            icon: "chevron_left"
            available: root.hourOffset>0
            onClicked: root.hourOffset=Math.max(0,root.hourOffset-3)
        }
        WeatherButton {
            objectName: "weatherNext"
            visible: root.hourlyExpanded
            icon: "chevron_right"
            available: root.hourOffset<root.maxOffset
            onClicked: root.hourOffset=Math.min(root.maxOffset,root.hourOffset+3)
        }
    }
    WeatherHourly {
        objectName: "weatherChart"
        Layout.fillWidth: true
        visible: root.hourlyExpanded && root.allHourly.length>0
        entries: root.allHourly
        offset: root.hourOffset
        windowSize: root.windowSize
        geometryScale: root.scaleOffset
        textPixels: root.bodyPixels
    }
    MenuText {
        Layout.fillWidth: true
        visible: root.hourlyExpanded && !root.allHourly.length
        text: qsTr("No hourly forecast available")
        font.pixelSize: root.bodyPixels*.82
        color: MenuStyle.muted
        horizontalAlignment: Text.AlignHCenter
    }
    Rule {Layout.topMargin:4*root.scaleOffset}
    MenuText {
        Layout.fillWidth: true
        Layout.bottomMargin: 4*root.scaleOffset
        horizontalAlignment: Text.AlignHCenter
        text: root.weather.loading ? qsTr("Updating…") : root.weather.hasWeather && root.observedTime ? qsTr("Updated %1").arg(root.observedTime.slice(0,10)===Qt.formatDate(new Date(),"yyyy-MM-dd")?root.observedTime.slice(11,16):root.observedTime) : qsTr("Weather data")
        font.pixelSize: root.bodyPixels*.82
        color: MenuStyle.muted
    }

    component Rule: Rectangle {
        Layout.fillWidth: true
        implicitHeight: 1
        color: MenuStyle.rule
    }
    component WeatherButton: Rectangle {
        id: button
        required property string icon
        property bool available: true
        property bool plain: false
        property bool spinning: false
        signal clicked
        implicitWidth: 34*root.scaleOffset
        implicitHeight: 34*root.scaleOffset
        radius: width/2
        color: plain?"transparent":MenuStyle.cardFill
        border.width: plain?0:1
        border.color: MenuStyle.rule
        opacity: available || spinning?1:.38
        activeFocusOnTab: available
        Accessible.role: Accessible.Button
        Accessible.name: icon==="refresh"?qsTr("Refresh weather"):icon==="chevron_left"?qsTr("Previous hours"):icon==="chevron_right"?qsTr("Next hours"):qsTr("Toggle hourly forecast")
        Accessible.onPressAction: if(available) clicked()
        Keys.onReturnPressed: if(available) clicked()
        Keys.onSpacePressed: if(available) clicked()
        StateLayer {radius:button.radius;disabled:!button.available;color:MenuStyle.ink;onClicked:button.clicked()}
        MaterialIcon {
            anchors.centerIn: parent
            text: button.icon
            color: MenuStyle.ink
            fontStyle.pointSize: 18*root.scaleOffset
            RotationAnimation on rotation {running:button.spinning;from:0;to:360;duration:1000;loops:Animation.Infinite}
        }
    }
    component Metric: Rectangle {
        id: metric
        required property string icon
        required property string label
        required property string value
        property color tint: "#91c8e8"
        Layout.fillWidth: true
        Layout.preferredWidth: 1
        Layout.fillHeight: true
        implicitHeight: Math.max(66*root.scaleOffset,metricText.implicitHeight+20*root.scaleOffset)
        radius: 16*root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: MenuStyle.rule
        RowLayout {
            anchors.fill: parent
            anchors.margins: 10*root.scaleOffset
            spacing: 9*root.scaleOffset
            MaterialIcon {
                text: metric.icon
                color: metric.tint
                fontStyle.pointSize: 25*root.scaleOffset
            }
            ColumnLayout {
                id: metricText
                Layout.fillWidth: true
                spacing: 2*root.scaleOffset
                MenuText {
                    Layout.fillWidth: true
                    text: metric.label
                    color: MenuStyle.muted
                    font.pixelSize: root.bodyPixels*.82
                    wrapMode: Text.WordWrap
                }
                MenuText {
                    Layout.fillWidth: true
                    text: metric.value
                    font.pixelSize: root.bodyPixels*1.05
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                }
            }
        }
    }
}
