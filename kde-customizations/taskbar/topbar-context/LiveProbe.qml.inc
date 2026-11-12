    TestCase { id: mouseTest; name: "TaskbarPointer"; when: false; property var saved }
    IpcHandler {
        target: "topbarTest-" + root.screen.name
        function prepare(): void {
            const node = GlobalConfig.forScreen(root.screen.name).bar;
            mouseTest.saved = {values: {position: node.position, persistent: node.persistent, showOnHover: node.showOnHover},
                globalPersistent: GlobalConfig.bar.persistent, globalHover: GlobalConfig.bar.showOnHover,
                overrides: [...node.overrides], unlocked: SplitBarSettings.taskbarUnlocked,
                dockScale: SplitBarSettings.dockScale, manual: root.visibilities.bar};
            node.position = "top";
            node.resetOption("persistent");
            node.resetOption("showOnHover");
            GlobalConfig.bar.persistent = true;
            GlobalConfig.bar.showOnHover = true;
            SplitBarSettings.setTaskbarUnlocked(false);
            root.visibilities.bar = false;
        }
        function restore(): void {
            close();
            const saved = mouseTest.saved;
            const node = GlobalConfig.forScreen(root.screen.name).bar;
            for (const key in saved.values) {
                if (saved.overrides.includes(key)) node[key] = saved.values[key];
                else node.resetOption(key);
            }
            GlobalConfig.bar.persistent = saved.globalPersistent;
            GlobalConfig.bar.showOnHover = saved.globalHover;
            SplitBarSettings.setTaskbarUnlocked(saved.unlocked);
            SplitBarSettings.setDockScale(saved.dockScale);
            root.visibilities.bar = saved.manual;
            // Flush restored overrides before the test restarts the shell.
            GlobalConfig.forScreen(root.screen.name).save();
            GlobalConfig.save();
        }
        function pointer(kind: string, x: real, y: real, button: int): void {
            const target = root.parent;
            if (kind === "click") mouseTest.mouseClick(target, x, y, button);
            if (kind === "press") mouseTest.mousePress(target, x, y, button);
            if (kind === "move") mouseTest.mouseMove(target, x, y, 20, button);
            if (kind === "release") mouseTest.mouseRelease(target, x, y, button);
        }
        function open(): void {
            root.popouts.currentName = "taskbarcontext";
            root.popouts.currentCenter = root.isHorizontal ? root.screen.width / 2 : root.screen.height / 2;
            root.popouts.hasCurrent = true;
        }
        function inspect(): string {
            const menu = root.popouts.current;
            const column = menu?.children.find(child => child.children?.length >= 5);
            return JSON.stringify({position:root.position, x:root.x,y:root.y,width:root.width,height:root.height,
                screenWidth:root.screen.width,screenHeight:root.screen.height,
                unlocked:SplitBarSettings.taskbarUnlocked,persistent:root.Config.bar.persistent,hover:root.Config.bar.showOnHover,
                visible:root.shouldBeVisible,moving:root.moving,dropEdge:root.dropEdge,open:root.popouts.hasCurrent,
                rows:column?.children.filter(child => child.text !== undefined).map(child => ({
                    text:child.text,checked:child.checked,point:child.mapToItem(root.parent,child.width/2,child.height/2)}))});
        }
        function windows(): string { return JSON.stringify(Kwin.windowList); }
        function closeWindow(address: string): void { Kwin.closeWindow(address); }
        function close(): void { root.popouts.hasCurrent = false; }
    }
