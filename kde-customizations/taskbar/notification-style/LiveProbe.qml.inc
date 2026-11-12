    TestCase { id: pointerTest; name: "NotificationPointer"; when: false }
    property var notificationTestItems: []
    property int notificationTestInvocations: 0
    property var notificationFrameSamples: []
    property real notificationLastFrame: 0
    property bool notificationSampling: false
    Connections {
        target: root.contentItem.Window.window
        function onFrameSwapped(): void {
            if (!root.notificationSampling) return;
            const now=Date.now();
            if (root.notificationLastFrame) root.notificationFrameSamples.push(now-root.notificationLastFrame);
            root.notificationLastFrame=now;
        }
    }
    IpcHandler {
        target: "notificationTest-" + root.screen.name
        function prepare(): void {
            const data = [
                {appName: "Steam", summary: "Downloading update", body: "2.4 / 3.5 GB", appIcon: "steam"},
                {appName: "Screen Capture", summary: "Screenshot saved", body: "Ready to view or share.", materialIcon: "screenshot_monitor"},
                {appName: "System", summary: "Updates available", body: "49 system updates are ready.", materialIcon: "arrow_upward", actions: [
                    {text: "View updates", invoke: () => { root.notificationTestInvocations++; }},
                    {text: "Later", invoke: () => { root.notificationTestInvocations++; }}
                ]}
            ];
            for (let i=0; i<data.length; i++) {
                const n=Notifs.addShellNotification(data[i]);
                Notifs.activeTargetOutput=root.screen.name;
                n.expireTimeout=120000;
                if (i===0) n.hints={value:68};
                n.popup=true;
                n.timer.restart();
                root.notificationTestItems.push(n);
            }
        }
        function inspect(): string {
            return JSON.stringify({screen:root.screen.name, visible:panels.notifications.visible,
                panel:{width:panels.notifications.width,height:panels.notifications.height},
                pool: {count:notificationPool.pooledPassCount,active:notificationPool.activePassCount,width:notificationPool.capacityWidth,height:notificationPool.capacityHeight},
                slots:notificationSmoke.instances.map(s => s.cardGeometry), invoked:root.notificationTestInvocations});
        }
        function pointer(kind: string, x: real, y: real): void {
            if (kind === "click") pointerTest.mouseClick(root.contentItem,x,y,Qt.LeftButton);
            else if (kind === "move") pointerTest.mouseMove(root.contentItem,x,y);
            else if (kind === "press") pointerTest.mousePress(root.contentItem,x,y,Qt.LeftButton);
            else if (kind === "release") pointerTest.mouseRelease(root.contentItem,x,y,Qt.LeftButton);
        }
        function sample(extraBlur: bool): void {
            notificationPool.suspended=!extraBlur;
            root.notificationFrameSamples=[];
            root.notificationLastFrame=0;
            root.notificationSampling=true;
        }
        function samples(): string {
            root.notificationSampling=false;
            return JSON.stringify(root.notificationFrameSamples);
        }
        function longText(): void {
            root.notificationTestItems[0].body="Langer deutscher Benachrichtigungstext mit einem Dateinamen, weiteren Details und einem Link: <a href='https://example.com'>Details ansehen</a>. Der gesamte Inhalt soll lesbar umbrechen und die folgenden Karten nach unten verschieben.";
        }
        function detail(): string {
            function walk(item) {
                const result={type:item.toString(),x:item.x,y:item.y,width:item.width,height:item.height};
                if(item.text!==undefined) result.text=item.text;
                if(item.expanded!==undefined) result.expanded=item.expanded;
                if(item.modelData?.timer) result.timerRunning=item.modelData.timer.running;
                result.children=(item.children || []).map(walk);return result;
            }
            return JSON.stringify(walk(panels.notifications));
        }
        function cleanup(): void { for (const n of root.notificationTestItems) n.close(); root.notificationTestItems=[]; }
    }

