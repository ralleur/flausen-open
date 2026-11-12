pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import QtQuick.Window
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Caelestia.Config
import Flausen.Settings
import qs.services
import qs.components
import qs.modules.nexus.flausen

FloatingWindow {
    id: win
    title: win.tr("flausen Task Manager")
    implicitWidth: Math.min(1410, (screen?.width ?? 1600)-80)
    implicitHeight: Math.min(1040, (screen?.height ?? 1200)-100)
    minimumSize.width: 1140; minimumSize.height: 680
    color: 'transparent'
    surfaceFormat.opaque: false
    Binding {target:win.contentItem.Window.window;property:'flags';value:Qt.Window | Qt.FramelessWindowHint;when:win.contentItem.Window.window!==null}
    BackgroundEffect.blurRegion: Region {
        Region { x:-10;y:-10;width:1;height:1 }
        Region { item:GlobalConfig.appearance.transparency.enabled && GlobalConfig.appearance.blur ? frame : null;radius:win.maximized ? 0 : 12 }
    }
    property var snapshot: ({processes:[], cards:[], count:0, threads:0, uptime:0, load:'—', updated:'', cores:[], detail:null})
    property var messages: ({})
    property string uiLanguage: ''
    property string uiLocale: 'en_US'
    property var startupRows: []
    property var serviceRows: []
    property var selected: null
    property var expanded: ({})
    property bool backgroundExpanded: false
    property bool initialSizeApplied: false
    property var processorHistoryModes: ({})
    property string sortKey: 'cpu'
    property bool descending: true
    property string page: 'processes'
    property string extra: ''
    property string message: ''
    property bool failed: false
    property bool connected: false
    property real receivedAt: 0
    property real refreshSeconds: 1
    property var pendingAction: null
    readonly property var detail: snapshot.detail
    readonly property var columns: [
        {name:win.tr("Name"),key:'name',width:0}, {name:win.tr("CPU"),key:'cpu',width:76},
        {name:win.tr("Memory"),key:'memory',width:92}, {name:win.tr("GPU"),key:'gpu',width:62},
        {name:win.tr("Read"),key:'read',width:86}, {name:win.tr("Write"),key:'write',width:86},
        {name:'Down',key:'down',width:74}, {name:'Up',key:'up',width:74}, {name:win.tr("PID"),key:'pid',width:64}].filter(c => win.width>=1320 || !['gpu','down','up'].includes(c.key))
    function tr(text) {return win.messages?.[text]??text;}
    function fitInitialSize() {
        if(initialSizeApplied || !snapshot.cards.length)return;
        const topRows=Math.ceil(snapshot.cards.length/resourceGrid.columns);
        const chartRows=Math.ceil(snapshot.cards.length/2);
        const cellColumns=Math.max(1,Math.floor((((win.width-56)/2)-36+8)/72));
        let extra=0;
        for(let row=0;row<chartRows;row++){
            const cards=snapshot.cards.slice(row*2,row*2+2);
            const rowHeight=Math.max(210,...cards.map(card=>card.processors?.length ? 100+Math.ceil(card.processors.length/cellColumns)*112+Math.max(0,Math.ceil(card.processors.length/cellColumns)-1)*8 : 210));
            extra+=rowHeight-210;
        }
        const needed=172+topRows*146+(topRows-1)*12+chartRows*210+(chartRows-1)*16+36+20+extra;
        win.contentItem.Window.window.height=Math.min(needed,(screen?.height??1200)-100);
        initialSizeApplied=true;
    }
    function requestClose() { Qt.quit(); }
    function raiseWindow() { win.contentItem.Window.window.requestActivate(); }
    function send(request) { if (backend.running) backend.write(JSON.stringify(request)+'\n'); }
    function bytes(value) { if(value===null || value===undefined)return '—'; const units=['B','KB','MB','GB','TB']; let i=0; while(value>=1024 && i<4){value/=1024;i++;} return (i>1 ? value.toFixed(1) : Math.round(value))+' '+units[i]; }
    function metric(row,key) { if(row.heading)return ''; if(key==='name')return row.name; if(key==='pid')return row.pid; if(key==='cpu')return row.cpu.toFixed(1)+'%'; if(key==='memory')return bytes(row.memory); if(key==='read'||key==='write')return row[key]===null?'—':bytes(row[key])+'/s'; return '—'; }
    function select(row) { selected={pid:row.pid,created:row.created}; extra=''; send({action:'select',identity:selected}); }
    function requestAction(action) { if(!selected)return; pendingAction={action:action,identity:{pid:selected.pid,created:selected.created},name:detail?.name??String(selected.pid)}; confirm.open(); }
    function rows() {
        let data=snapshot.processes.filter(p => (filter.currentIndex===0 || (filter.currentIndex===1 ? p.own : !p.own)) && (p.name+' '+p.rawName+' '+p.pid+' '+p.user).toLowerCase().includes(search.text.toLowerCase()));
        data.sort((a,b) => {const av=a[sortKey],bv=b[sortKey]; return (typeof av==='string'?av.localeCompare(bv):(av??-1)-(bv??-1))*(descending?-1:1);});
        let result=[];
        const append = p => {result.push(Object.assign({},p,{child:false}));if(expanded[p.pid])p.children.forEach(c=>result.push(Object.assign({},c,{child:true})));};
        data.filter(p=>p.application).forEach(append);
        const background=data.filter(p=>!p.application);
        if(background.length)result.push({heading:true,name:win.tr("Background & system"),pid:-1,count:background.length});
        if(backgroundExpanded)background.forEach(append);
        return result;
    }
    function selectExtra(value) { extra=extra===value?'':value; send({action:'select',identity:selected,extra:extra}); }
    function changePage(value) { page=value; message=''; if(page==='startup')send({action:'startup'}); if(page==='services')send({action:'services'}); }
    GraphClock { id: graphTimeline; interval: win.refreshSeconds*1000 }
    Process {
        id: backend
        command: ['/usr/bin/python3', Qt.resolvedUrl('../backend.py').toString().replace('file://','')]
        stdinEnabled: true; running: true
        stdout: SplitParser {
            onRead: line => {
                try {
                    const data=JSON.parse(line);
                    if(data.type==='snapshot'){
                        if(data.language!==win.uiLanguage){win.messages=data.translations??{};win.uiLanguage=data.language??'en';}
                        win.uiLocale=data.locale??'en_US';
                        graphTimeline.accept(data);win.snapshot=data;win.connected=true;win.receivedAt=Date.now();
                        if(!win.initialSizeApplied)Qt.callLater(win.fitInitialSize);
                        if(!win.selected){const apps=data.processes.filter(p=>p.application).sort((a,b)=>b.memory-a.memory);if(apps.length)win.select(apps[0]);}
                    }
                    else if(data.type==='startup')win.startupRows=data.rows;
                    else if(data.type==='services')win.serviceRows=data.rows;
                    else {win.message=data.message;win.failed=data.type==='error';if(data.type==='notice'&&win.page==='startup')win.send({action:'startup'});if(data.type==='notice'&&win.page==='services')win.send({action:'services'});}
                } catch(error) {win.message=win.tr("Could not read system data.");win.failed=true;}
            }
        }
        onExited: {win.connected=false;win.message=win.tr("System monitor stopped. Reconnect to continue.");win.failed=true;}
    }
    Timer { interval: 4000; repeat: true; running: true; onTriggered: {if(win.receivedAt && Date.now()-win.receivedAt>Math.max(12000,win.refreshSeconds*3000)){win.connected=false;win.message=win.tr("No recent system data.");win.failed=true;}} }
    Shortcut { sequence: 'Ctrl+F'; onActivated: search.forceActiveFocus() }
    Shortcut { sequence: 'Escape'; onActivated: {if(confirm.opened)confirm.close();else if(search.text)search.clear();else win.requestClose();} }
    onVisibleChanged: {if(!visible)Qt.quit();}
    Rectangle {
        id: frame
        anchors.fill: parent; radius: win.maximized ? 0 : 12
        color: GlobalConfig.appearance.transparency.enabled ? Qt.alpha(FlausenStyle.surface,.96) : FlausenStyle.surface
        border.width: 1; border.color: FlausenStyle.line
        clip: true
        WindowFrame { }
        ColumnLayout {
            anchors.fill: parent; spacing: 0
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 58
                MouseArea { anchors.fill: parent; onPressed: win.startSystemMove() }
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 24; anchors.rightMargin: 10; spacing: 8
                    Image { id: appLogo; source: Qt.resolvedUrl('../icon.png'); sourceSize.width: 96; sourceSize.height: 96; Layout.preferredWidth: 32; Layout.preferredHeight: 32; mipmap: true }
                    TMText { text: win.tr("Task Manager"); size: 20; color: FlausenStyle.text; Layout.leftMargin: 5; Layout.rightMargin: 24 }
                    Repeater {
                        model: [{id:'processes',name:win.tr('Processes'),icon:'format_list_bulleted'},{id:'performance',name:win.tr('Performance'),icon:'monitoring'},{id:'startup',name:win.tr('Startup'),icon:'power_settings_new'},{id:'services',name:win.tr('Services'),icon:'layers'}]
                        TMButton {
                            id: tab; required property var modelData
                            Layout.preferredWidth: 142; selected: win.page===modelData.id
                            onClicked: win.changePage(modelData.id)
                            contentItem: RowLayout {
                                spacing: 10
                                TMIcon { text: tab.modelData.icon; color: FlausenStyle.text; font.pixelSize: 23 }
                                TMText { text: tab.modelData.name; size: 15; color: FlausenStyle.text }
                            }
                        }
                    }
                    Item { Layout.fillWidth: true }
                    TMButton { text:'⚙'; Accessible.name:win.tr("Display options"); onClicked: options.open(); C.ToolTip.visible:hovered; C.ToolTip.text:win.tr("Display options") }
                    WindowControl { id:closeButton;objectName:'taskManagerClose';palette.windowText:FlausenStyle.text; controlAction:'close'; description:win.tr(qsTranslate("Flausen", "Close")); onClicked:win.requestClose() }
                }
            }
            Rectangle { Layout.fillWidth:true; implicitHeight:1; color:FlausenStyle.line }
            GridLayout {
                id: resourceGrid
                Layout.fillWidth:true; Layout.margins:20; columnSpacing:12;rowSpacing:12
                readonly property int capacity:Math.max(1,Math.floor((width+12)/232))
                columns:Math.min(capacity,Math.max(1,Math.ceil(win.snapshot.cards.length/Math.max(1,Math.ceil(win.snapshot.cards.length/capacity)))))
                Repeater { model:win.snapshot.cards; ResourceCard {required property var modelData;translate:win.tr; graphClock:graphTimeline;cardData:modelData; Layout.fillWidth:true; Layout.minimumWidth:0; Layout.preferredWidth:1; Layout.preferredHeight:146} }
            }
            Rectangle {
                visible:win.message!==''; Layout.fillWidth:true; Layout.leftMargin:20; Layout.rightMargin:20; Layout.bottomMargin:12
                implicitHeight:notice.implicitHeight+18; radius:8; color:Qt.alpha(win.failed?'#f47c69':FlausenStyle.accent,.12)
                RowLayout {
                    anchors.fill:parent; anchors.margins:9
                    TMText { id:notice; text:win.message; size:13; color:win.failed?'#f47c69':FlausenStyle.text; Layout.fillWidth:true; wrapMode:Text.Wrap }
                    TMButton { visible:!backend.running; text:win.tr("Reconnect"); onClicked:{backend.running=true;win.message='';} }
                    TMButton { text:'×'; onClicked:win.message='' }
                }
            }
            RowLayout {
                visible:win.page==='processes'; Layout.fillWidth:true; Layout.fillHeight:true; Layout.leftMargin:20; Layout.rightMargin:20; Layout.bottomMargin:16; spacing:14
                ColumnLayout {
                    Layout.fillWidth:true; Layout.fillHeight:true; spacing:12
                    RowLayout {
                        Layout.fillWidth:true; spacing:12
                        Rectangle {
                            Layout.fillWidth:true; implicitHeight:40; radius:20; color:FlausenStyle.card; border.color:search.activeFocus?FlausenStyle.accent:FlausenStyle.line
                            TMIcon { anchors.left:parent.left; anchors.leftMargin:14; anchors.verticalCenter:parent.verticalCenter; text:'search'; font.pixelSize:22; color:FlausenStyle.secondary }
                            C.TextField { id:search; anchors.fill:parent; leftPadding:44; rightPadding:16; placeholderText:win.tr("Search processes…"); color:FlausenStyle.text; placeholderTextColor:FlausenStyle.secondary; font.family:MenuStyle.fontFamily; font.pixelSize:16; selectByMouse:true; background:Item{} }
                        }
                        C.ComboBox { id:filter; model:[win.tr("All processes"),win.tr("My processes"),win.tr("Other users")]; implicitWidth:195; implicitHeight:40; palette.window:FlausenStyle.card; palette.text:FlausenStyle.text; palette.button:FlausenStyle.card; palette.buttonText:FlausenStyle.text; font.family:MenuStyle.fontFamily; font.pixelSize:14 }
                        TMButton { text:win.refreshSeconds+' s  ↻'; Accessible.name:win.tr("Change refresh interval"); onClicked:options.open() }
                    }
                    RowLayout {
                        Layout.fillWidth:true; spacing:0
                        Repeater {
                            model:win.columns
                            TMButton {
                                required property var modelData
                                Layout.fillWidth:modelData.key==='name'; Layout.preferredWidth:modelData.width; implicitHeight:34
                                textAlignment:modelData.key==='name'?Text.AlignLeft:Text.AlignHCenter
                                text:modelData.name+(win.sortKey===modelData.key?(win.descending?' ↓':' ↑'):'')
                                enabled:!['gpu','down','up'].includes(modelData.key)
                                onClicked:{if(win.sortKey===modelData.key)win.descending=!win.descending;else{win.sortKey=modelData.key;win.descending=win.sortKey!=='name';}}
                            }
                        }
                    }
                    Rectangle { Layout.fillWidth:true; implicitHeight:1; color:FlausenStyle.line }
                    ListView {
                        id:processList
                        Layout.fillWidth:true; Layout.fillHeight:true; clip:true; model:win.rows(); reuseItems:true
                        C.ScrollBar.vertical:C.ScrollBar{}
                        boundsBehavior:Flickable.StopAtBounds
                        delegate:Rectangle {
                            id:row
                            required property var modelData
                            width:processList.width; height:42; radius:7
                            color:modelData.heading?'transparent':win.selected?.pid===modelData.pid && win.selected?.created===modelData.created ? FlausenStyle.selected : rowHover.hovered?Qt.alpha(FlausenStyle.secondary,.07):'transparent'
                            HoverHandler { id:rowHover }
                            TapHandler { enabled:!row.modelData.heading; onTapped:win.select(row.modelData) }
                            TMButton {
                                visible:row.modelData.heading??false
                                anchors.fill:parent
                                textAlignment:Text.AlignLeft
                                text:(win.backgroundExpanded?'⌄   ':'›   ')+row.modelData.name+' ('+(row.modelData.count??0)+')'
                                Accessible.name:win.tr("Background and system")
                                Accessible.role:Accessible.Button
                                Accessible.description:win.backgroundExpanded?win.tr("Expanded. Activate to collapse."):win.tr("Collapsed. Activate to expand.")
                                onClicked:win.backgroundExpanded=!win.backgroundExpanded
                            }
                            RowLayout {
                                anchors.fill:parent; spacing:0; visible:!row.modelData.heading
                                Item {
                                    Layout.fillWidth:true; Layout.fillHeight:true
                                    RowLayout {
                                        anchors.fill:parent; anchors.leftMargin:row.modelData.child?28:0; spacing:8
                                        TMButton { visible:!row.modelData.child; text:(row.modelData.count??0)>1?(win.expanded[row.modelData.pid]?'⌄':'›'):''; implicitWidth:28; implicitHeight:34; enabled:(row.modelData.count??0)>1; onClicked:{let state=Object.assign({},win.expanded);state[row.modelData.pid]=!state[row.modelData.pid];win.expanded=state;} }
                                        Image { source:Quickshell.iconPath(row.modelData.icon,'application-x-executable'); sourceSize.width:30; sourceSize.height:30; Layout.preferredWidth:30; Layout.preferredHeight:30 }
                                        TMText { text:row.modelData.name+((row.modelData.count??0)>1?' ('+row.modelData.count+')':''); color:FlausenStyle.text; Layout.fillWidth:true; size:15; C.ToolTip.visible:rowHover.hovered; C.ToolTip.text:(row.modelData.rawName??'')+' · '+(row.modelData.user??'') }
                                    }
                                }
                                Repeater {
                                    model:win.columns.slice(1)
                                    TMText { required property var modelData; text:win.metric(row.modelData,modelData.key); size:15; color:modelData.key==='gpu'||modelData.key==='down'||modelData.key==='up'?FlausenStyle.secondary:FlausenStyle.text; Layout.preferredWidth:modelData.width; horizontalAlignment:Text.AlignRight; rightPadding:10 }
                                }
                            }
                            Rectangle { anchors.bottom:parent.bottom; x:12; width:parent.width-24; height:1; color:FlausenStyle.line; opacity:.55 }
                        }
                        TMText { anchors.centerIn:parent; visible:processList.count===0; text:win.connected?win.tr("No matching processes"):win.tr("Loading system data…"); color:FlausenStyle.secondary }
                    }
                }
                Rectangle { Layout.fillHeight:true; implicitWidth:1; color:FlausenStyle.line }
                Rectangle {
                    id:inspectorPanel
                    Layout.preferredWidth:326; Layout.fillHeight:true; radius:14; color:Qt.alpha(FlausenStyle.card,.65); border.color:FlausenStyle.line
                    C.ScrollView {
                        id:inspectorScroll
                        anchors.fill:parent;anchors.margins:14;anchors.bottomMargin:68
                        clip:true;contentWidth:availableWidth
                        ColumnLayout {
                        width:inspectorScroll.availableWidth;spacing:8
                        RowLayout {
                            Layout.fillWidth:true; spacing:14
                            Image { visible:!!win.detail&&!win.detail.exited; source:Quickshell.iconPath(win.detail?.icon??'application-x-executable'); Layout.preferredWidth:54; Layout.preferredHeight:54; sourceSize.width:54; sourceSize.height:54 }
                            ColumnLayout {
                                Layout.fillWidth:true; spacing:3
                                TMText { text:win.detail?.exited?win.tr("Process exited"):win.detail?.name??win.tr("Process inspector"); size:22; color:FlausenStyle.text; Layout.fillWidth:true }
                                TMText { text:win.detail&&!win.detail.exited?'●  '+({running:win.tr("Running"),sleeping:win.tr("Active"),idle:win.tr("Ready"),stopped:win.tr("Suspended"),zombie:win.tr("Zombie")}[win.detail.status]??win.detail.status):win.tr("Select a process on the left"); size:13; color:win.detail&&!win.detail.exited?'#8dcf83':FlausenStyle.secondary; Layout.fillWidth:true }
                                TMText { visible:!!win.detail; text:win.tr("Individual process · PID ")+(win.detail?.pid??''); size:13; color:FlausenStyle.secondary }
                            }
                        }
                        Repeater {
                            model:win.detail&&!win.detail.exited?[{title:win.tr("CPU"),value:win.detail.cpu.toFixed(1)+'%',values:win.detail.cpuHistory,color:'#479cff',max:100},{title:win.tr("Memory"),value:win.bytes(win.detail.memory),values:win.detail.memoryHistory,color:'#a7cf7c',max:0}]:[]
                            Rectangle {
                                id:detailChart; required property var modelData
                                Layout.fillWidth:true; implicitHeight:64; radius:12; color:FlausenStyle.card; border.color:FlausenStyle.line; clip:true
                                RowLayout { anchors.top:parent.top; anchors.left:parent.left; anchors.right:parent.right; anchors.margins:10; TMText { text:detailChart.modelData.title+'  '+detailChart.modelData.value; color:FlausenStyle.text; size:14; Layout.fillWidth:true } TMText {text:win.tr("60 samples");size:11;color:FlausenStyle.secondary} }
                                Sparkline { graphClock:graphTimeline;seriesId:'process:'+win.detail.pid+':'+win.detail.created+':'+(detailChart.modelData.title===win.tr("CPU")?'cpu':'memory');anchors.left:parent.left; anchors.right:parent.right; anchors.bottom:parent.bottom; height:35; values:detailChart.modelData.values; ink:detailChart.modelData.color; ceiling:detailChart.modelData.max }
                            }
                        }
                        ColumnLayout {
                            Layout.fillWidth:true; spacing:0
                            Repeater {
                                model:win.detail&&!win.detail.exited?[
                                    [win.tr("GPU"),'—'],[win.tr("User"),win.detail.user],[win.tr("Threads"),win.detail.threads],[win.tr("Priority"),'Nice '+win.detail.priority],[win.tr("Started"),win.detail.started],[win.tr("Path"),win.detail.path]]:[]
                                Item {
                                    id:metadata;required property var modelData
                                    Layout.fillWidth:true;implicitHeight:25
                                    RowLayout {
                                        anchors.fill:parent;anchors.bottomMargin:3
                                        TMText {text:metadata.modelData[0];size:13;color:FlausenStyle.secondary;Layout.preferredWidth:96}
                                        TMText {text:String(metadata.modelData[1]);size:13;color:FlausenStyle.text;Layout.fillWidth:true;C.ToolTip.visible:metaHover.hovered;C.ToolTip.text:String(metadata.modelData[1]);HoverHandler{id:metaHover}}
                                    }
                                    Rectangle {anchors.bottom:parent.bottom;width:parent.width;height:1;color:FlausenStyle.line;opacity:.7}
                                }
                            }
                        }
                        TMButton { visible:!!win.detail&&!win.detail.exited; Layout.fillWidth:true; text:(win.extra==='files'?'⌄':'›')+'   '+win.tr('Open files'); selected:win.extra==='files'; onClicked:win.selectExtra('files') }
                        TMButton { visible:!!win.detail&&!win.detail.exited; Layout.fillWidth:true; text:(win.extra==='connections'?'⌄':'›')+'   '+win.tr('Connections'); selected:win.extra==='connections'; onClicked:win.selectExtra('connections') }
                        ListView {
                            Layout.fillWidth:true; Layout.preferredHeight:140; clip:true
                            visible:win.extra!=='' && !!win.detail && !win.detail.exited
                            model:win.extra==='files'?(win.detail?.files??[]):(win.detail?.connections??[])
                            C.ScrollBar.vertical:C.ScrollBar{}
                            delegate:Column {
                                required property var modelData
                                width:ListView.view.width; spacing:3; height:48
                                TMText {width:parent.width;text:modelData.name;size:12;color:FlausenStyle.text;C.ToolTip.visible:extraHover.hovered;C.ToolTip.text:modelData.name;HoverHandler{id:extraHover}}
                                TMText {width:parent.width;text:modelData.value;size:11;color:FlausenStyle.secondary}
                            }
                            TMText { anchors.centerIn:parent; width:parent.width; horizontalAlignment:Text.AlignHCenter; wrapMode:Text.Wrap; visible:parent.count===0; text:win.detail?.extraError||win.tr(qsTranslate("Flausen", "No entries")); size:12; color:FlausenStyle.secondary }
                        }
                        TMText { visible:!!win.detail&&!win.detail.exited; text:win.tr("Per-process GPU and network: unavailable"); size:11; color:FlausenStyle.secondary; Layout.fillWidth:true }

                        }
                    }
                        RowLayout {
                            anchors.left:parent.left;anchors.right:parent.right;anchors.bottom:parent.bottom;anchors.margins:14
                            TMButton { Layout.fillWidth:true; text:win.tr("End process"); danger:true; enabled:win.connected&&!!win.detail&&!win.detail.exited&&win.detail.own; onClicked:win.requestAction('terminate') }
                            TMButton { text:'•••'; enabled:win.connected&&!!win.detail&&!win.detail.exited&&win.detail.own; Accessible.name:win.tr("More process actions"); onClicked:processMenu.open() }
                        }
                }
            }
            C.ScrollView {
                id: performanceView
                visible:win.page==='performance'; Layout.fillWidth:true; Layout.fillHeight:true; Layout.leftMargin:20; Layout.rightMargin:20; Layout.bottomMargin:20; clip:true
                contentWidth:availableWidth
                ColumnLayout {
                    width:parent.width; spacing:16
                    GridLayout {
                        columns:2; columnSpacing:16; rowSpacing:16; Layout.fillWidth:true
                        Repeater {
                            model:win.snapshot.cards
                            Rectangle {
                                id:bigChart; required property var modelData
                                Layout.fillWidth:true; Layout.preferredWidth:1; implicitHeight:Math.max(210,processorMeters.visible?processorMeters.implicitHeight+100:210); radius:14; color:FlausenStyle.card; border.color:FlausenStyle.line
                                TMText { x:18;y:14;width:parent.width-36-(modeToggle.visible?40:0);text:bigChart.modelData.name+'   '+bigChart.modelData.value;size:19;color:FlausenStyle.text }
                                TMButton {
                                    id:modeToggle
                                    objectName:'processorMode-'+bigChart.modelData.id
                                    visible:['cpu','gpu'].includes(bigChart.modelData.kind)
                                    anchors.right:parent.right;anchors.top:parent.top;anchors.rightMargin:12;anchors.topMargin:10
                                    implicitWidth:32;implicitHeight:32
                                    selected:processorMeters.historyMode
                                    Accessible.name:processorMeters.historyMode?win.tr("Show segment bars for each unit"):win.tr("Show history for each unit")
                                    C.ToolTip.visible:hovered
                                    C.ToolTip.delay:400
                                    C.ToolTip.text:Accessible.name
                                    contentItem:TMIcon {text:processorMeters.historyMode?'bar_chart':'show_chart';font.pixelSize:20;color:FlausenStyle.secondary;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
                                    onClicked:{const modes=Object.assign({},win.processorHistoryModes);modes[bigChart.modelData.id]=!processorMeters.historyMode;win.processorHistoryModes=modes;}
                                }
                                TMText { x:18;y:43;width:parent.width-36;text:bigChart.modelData.device??'';visible:text.length>0;size:12;color:FlausenStyle.secondary;C.ToolTip.visible:deviceHover.hovered;C.ToolTip.text:text;HoverHandler{id:deviceHover} }
                                TMText { x:18;y:62;width:parent.width-36;text:bigChart.modelData.detail+(bigChart.modelData.kind==='cpu'?' · '+win.tr('%1 cores / %2 threads').arg(bigChart.modelData.processors?.length??0).arg(win.snapshot.cores.length):'');size:13;color:FlausenStyle.secondary }
                                Sparkline { graphClock:graphTimeline;seriesId:bigChart.modelData.id;objectName:'performanceHistory-'+bigChart.modelData.id;visible:!['cpu','gpu'].includes(bigChart.modelData.kind); x:12;y:88;width:parent.width-24;height:parent.height-100;values:bigChart.modelData.history;ink:bigChart.modelData.color;ceiling:bigChart.modelData.kind==='network'?0:100 }
                                SegmentMeters {id:processorMeters;translate:win.tr;graphClock:graphTimeline;seriesId:bigChart.modelData.id;historyMode:win.processorHistoryModes[bigChart.modelData.id]??true;objectName:'performanceProcessors-'+bigChart.modelData.id;x:18;y:88;width:parent.width-36;height:implicitHeight;visible:['cpu','gpu'].includes(bigChart.modelData.kind);units:bigChart.modelData.processors??[];ink:bigChart.modelData.color}
                            }
                        }

                    }
                    TMText {text:win.tr("CPU: each physical core, averaged across its threads · GPU: available engines · History: 60 samples");size:13;color:FlausenStyle.secondary;Layout.fillWidth:true}
                }
            }
            ColumnLayout {
                visible:win.page==='startup'||win.page==='services'; Layout.fillWidth:true;Layout.fillHeight:true;Layout.leftMargin:20;Layout.rightMargin:20;Layout.bottomMargin:20;spacing:14
                RowLayout {
                    Layout.fillWidth:true
                    ColumnLayout {
                        Layout.fillWidth:true
                        TMText {text:win.page==='startup'?win.tr("Start at sign-in"):win.tr("User services");size:24;color:FlausenStyle.text}
                        TMText {text:win.page==='startup'?win.tr("XDG startup entries. Changes take effect at the next sign-in."):win.tr("Services in your systemd session");size:13;color:FlausenStyle.secondary}
                    }
                    TMButton{text:win.tr("Refresh");onClicked:win.send({action:win.page==='startup'?'startup':'services'})}
                }
                ListView {
                    id:otherList
                    Layout.fillWidth:true;Layout.fillHeight:true;clip:true;spacing:6;C.ScrollBar.vertical:C.ScrollBar{}
                    model:win.page==='startup'?win.startupRows:win.serviceRows
                    delegate:Rectangle {
                        id:entry;required property var modelData
                        width:otherList.width;height:70;radius:10;color:FlausenStyle.card;border.color:FlausenStyle.line
                        RowLayout {
                            anchors.fill:parent;anchors.margins:12;spacing:14
                            Image {source:Quickshell.iconPath(entry.modelData.icon??'system-run');Layout.preferredWidth:34;Layout.preferredHeight:34;sourceSize.width:34;sourceSize.height:34}
                            ColumnLayout {
                                Layout.fillWidth:true;spacing:4
                                TMText{text:entry.modelData.name;size:16;color:FlausenStyle.text;Layout.fillWidth:true}
                                TMText{text:entry.modelData.description||entry.modelData.command||'';size:12;color:FlausenStyle.secondary;Layout.fillWidth:true}
                            }
                            TMText{visible:win.page==='services';text:win.tr(entry.modelData.status??'');size:13;color:entry.modelData.active==='active'?'#8dcf83':FlausenStyle.secondary}
                            TMButton{visible:win.page==='startup';text:entry.modelData.enabled?win.tr("Enabled"):win.tr("Disabled");selected:entry.modelData.enabled??false;onClicked:win.send({action:'startup-toggle',name:entry.modelData.id,enabled:!entry.modelData.enabled})}
                            TMButton{visible:win.page==='services';text:entry.modelData.active==='active'?win.tr(qsTranslate("Flausen", "Stop")):win.tr(qsTranslate("Flausen", "Start"));onClicked:{win.pendingAction={action:'service',name:entry.modelData.name,operation:entry.modelData.active==='active'?'stop':'start'};confirm.open();}}
                        }
                    }
                    TMText{anchors.centerIn:parent;visible:otherList.count===0;text:win.tr(qsTranslate("Flausen", "No entries"));color:FlausenStyle.secondary}
                }
            }
            Rectangle { Layout.fillWidth:true;implicitHeight:1;color:FlausenStyle.line }
            RowLayout {
                Layout.fillWidth:true;Layout.preferredHeight:52;Layout.leftMargin:24;Layout.rightMargin:24;spacing:20
                TMText{text:win.tr('%1 processes').arg(win.snapshot.count);size:13;color:FlausenStyle.text}
                Rectangle{implicitWidth:1;implicitHeight:18;color:FlausenStyle.line}
                TMText{text:Math.round(win.snapshot.threads).toLocaleString(Qt.locale(win.uiLocale), 'f', 0)+' '+win.tr('threads');size:13;color:FlausenStyle.text}
                Rectangle{implicitWidth:1;implicitHeight:18;color:FlausenStyle.line}
                TMText{text:win.tr('Uptime')+' '+Math.floor(win.snapshot.uptime/86400)+' d '+Math.floor(win.snapshot.uptime%86400/3600)+' h';size:13;color:FlausenStyle.text}
                Rectangle{implicitWidth:1;implicitHeight:18;color:FlausenStyle.line}
                TMText{text:win.tr('Load')+' '+win.snapshot.load;size:13;color:FlausenStyle.text}
                Item{Layout.fillWidth:true}
                TMText{text:win.connected?win.tr('Updated')+' '+win.snapshot.updated:win.tr('Connecting…');size:12;color:FlausenStyle.secondary}
            }
        }
    }
    C.Menu {
        id:options
        x:win.width-width-20;y:58
        C.MenuItem{text:win.tr("Refresh every 0.5 s");onTriggered:{win.refreshSeconds=.5;win.send({action:'interval',value:.5});}}
        C.MenuItem{text:win.tr("Refresh every second");onTriggered:{win.refreshSeconds=1;win.send({action:'interval',value:1});}}
        C.MenuItem{text:win.tr("Refresh every 2 s");onTriggered:{win.refreshSeconds=2;win.send({action:'interval',value:2});}}
        C.MenuItem{text:win.tr("Refresh every 5 s");onTriggered:{win.refreshSeconds=5;win.send({action:'interval',value:5});}}
    }
    C.Menu {
        id:processMenu
        x:win.width-width-24;y:win.height-height-80
        C.MenuItem{text:win.tr("Suspend process");onTriggered:win.requestAction('stop')}
        C.MenuItem{text:win.tr("Resume process");onTriggered:win.requestAction('resume')}
        C.MenuSeparator{}
        C.MenuItem{text:win.tr("Force quit (SIGKILL)");onTriggered:win.requestAction('kill')}
    }
    C.Dialog {
        id:confirm
        anchors.centerIn:parent;modal:true;width:480;padding:24
        background:Rectangle{radius:14;color:FlausenStyle.card;border.color:FlausenStyle.line}
        contentItem:ColumnLayout {
            spacing:18
            TMText {text:win.pendingAction?.action==='service'?win.tr("Change service?"):win.pendingAction?.action==='stop'?win.tr("Suspend process?"):win.pendingAction?.action==='resume'?win.tr("Resume process?"):win.tr("End process?");size:23;color:FlausenStyle.text;Layout.fillWidth:true}
            TMText {text:(win.pendingAction?.name??'')+(win.pendingAction?.action==='terminate'||win.pendingAction?.action==='kill'?'\n'+win.tr('Unsaved work may be lost.'):'');wrapMode:Text.Wrap;size:14;color:FlausenStyle.secondary;Layout.fillWidth:true}
            RowLayout {Layout.fillWidth:true;Item{Layout.fillWidth:true} TMButton{text:win.tr(qsTranslate("Flausen", "Cancel"));onClicked:confirm.close()} TMButton{text:win.tr("Confirm");danger:true;onClicked:{win.send(win.pendingAction);confirm.close();}}}
        }
    }
    Repeater {
        model:[Qt.TopEdge,Qt.BottomEdge,Qt.LeftEdge,Qt.RightEdge,Qt.TopEdge|Qt.LeftEdge,Qt.TopEdge|Qt.RightEdge,Qt.BottomEdge|Qt.LeftEdge,Qt.BottomEdge|Qt.RightEdge]
        MouseArea {
            required property int modelData
            readonly property bool atLeft:(modelData&Qt.LeftEdge)!==0
            readonly property bool atRight:(modelData&Qt.RightEdge)!==0
            readonly property bool atTop:(modelData&Qt.TopEdge)!==0
            readonly property bool atBottom:(modelData&Qt.BottomEdge)!==0
            readonly property bool corner:(atLeft||atRight)&&(atTop||atBottom)
            z:30;enabled:!win.maximized
            width:corner?8:(atLeft||atRight)?5:parent.width-16;height:corner?8:(atTop||atBottom)?5:parent.height-16
            x:atRight?parent.width-width:atLeft?0:8;y:atBottom?parent.height-height:atTop?0:8
            cursorShape:corner?((atLeft&&atTop)||(atRight&&atBottom)?Qt.SizeFDiagCursor:Qt.SizeBDiagCursor):(atLeft||atRight)?Qt.SizeHorCursor:Qt.SizeVerCursor
            onPressed:win.startSystemResize(modelData)
        }
    }
}
