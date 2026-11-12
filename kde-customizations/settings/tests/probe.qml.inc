    // Temporary live-test hook; removed by live_check.py in its finally block.
    IpcHandler {
        target: "flausenSettingsTest"
        function inspect(): string {
            const page = testPages.currentItem;
            const leaf = page?.currentItem ?? page;
            return JSON.stringify({frameRadius:root.frameRadius, shadow:nativeFrame.shadowCreated, frameless: !!(root.Window.window.flags & Qt.FramelessWindowHint), maximized: WindowFactory.openWindow.maximized, minimized: Kwin.windowList.find(w => w.title === WindowFactory.openWindow.title)?.minimized ?? WindowFactory.openWindow.minimized, page:root.nState.currentPageIdx, title:leaf?.title ?? "", busy:leaf?.themeProcess?.running ?? false, subpages:root.nState.subPageIdxStack.length, light:Colours.light, scheme:Colours.scheme,
                windows:Kwin.windowList.map(w=>({address:w.address,title:w.title,app:w.class})), auto:GlobalConfig.services.autoSchemeEnabled, transparency:GlobalConfig.appearance.transparency.enabled,
                animations:GlobalConfig.appearance.anim.enabled, scale:GlobalConfig.appearance.font.scale,
                module:root.nState.systemModule, moduleTitle:root.nState.systemTitle, moduleReady:systemPage.backend.ready, moduleError:systemPage.backend.error, moduleDirty:systemPage.backend.needsSave, moduleDepth:systemPage.backend.depth, confirm:leaveDialog.opened,
                query:root.nState.searchQuery, search:PageRegistry.fuzzyEntries(root.nState.searchQuery).map(e=>({label:e.settingLabel,page:e.pageIdx,module:e.systemModule || ''}))});
        }
        function accountObject(name: string): var {
            const seen = new Set();
            function find(item) {
                if (!item || seen.has(item)) return null;
                seen.add(item);
                if (item.objectName === name) return item;
                for (const child of [...(item.data ?? []), ...(item.children ?? [])]) {
                    const found = find(child); if (found) return found;
                }
                return null;
            }
            return find(root);
        }
        function accountFacts(): string {
            const image = accountObject("accountAvatarImage");
            const picker = accountObject("accountPicturePicker");
            return JSON.stringify({source:image?.source.toString(), ready:image?.status === Image.Ready, picker:picker?.opened ?? false});
        }
        function accountAction(action: string): bool {
            if (action === "cancel") { accountObject("accountPicturePicker").reject(); return true; }
            const button = accountObject(action === "picture" ? "accountAvatarButton" : "accountSettingsButton");
            if (!button || !button.enabled) return false;
            button.clicked(); return true;
        }
        function windowControl(action: string): bool {
            function find(item) {
                if (item.controlAction === action && typeof item.clicked === "function") return item;
                for (const child of item.children ?? []) { const found = find(child); if (found) return found; }
                return null;
            }
            const button = find(root);
            if (!button) return false;
            button.clicked();
            return true;
        }
        function restoreWindow(): void {
            WindowFactory.openWindow.minimized = false;
            const target = Kwin.windowList.find(w => w.title === WindowFactory.openWindow.title);
            if (target?.address) Kwin.focusWindow(target.address);
        }
        function click(label: string): bool {
            function find(item) {
                if(!item || !item.visible)return null;
                if (item.text === label && typeof item.clicked === "function") return item;
                for (const child of item.children ?? []) { const found=find(child); if(found)return found; }
                return null;
            }
            const item=find(root);
            if(!item)return false;
            item.clicked();
            return true;
        }
        function toggle(label: string): bool {
            function find(item) {
                if (item.text === label && typeof item.toggle === "function") return item;
                for (const child of item.children ?? []) { const found=find(child); if(found)return found; }
                return null;
            }
            const item=find(root);
            if(!item)return false;
            item.toggle(); item.toggled(); return true;
        }
        function polishForAudit(pageWidth: int): void {
            if(pageWidth>0 && systemPage.backend.page)systemPage.backend.page.width=pageWidth;
            function polish(item){
                if(!item)return;
                if(typeof item.ensurePolished === "function")item.ensurePolished();
                for(const child of item.children ?? [])polish(child);
            }
            for(let pass=0;pass<5;pass++)polish(root);
        }
        function visualAudit(): string {
            try {
            // Force an actual frame, not just the pre-render layout state.
            screenshotTest.grabImage(root);
            const base=root.nState.systemModule ? systemPage.backend.page : testPages;
            const findings=[];let examined=0;
            function visit(item) {
                if(!item || !item.visible)return;
                if(item.background !== undefined && item.contentItem !== undefined && item.width>0 && item.height>0) {
                    examined++;
                    let card=item.parent;
                    while(card && card.showClickFeedback === undefined && !(card.radius>=12 && card.border?.width>0 && card.width>=item.width))card=card.parent;
                    if(card) {
                        const box=card.background ?? card;
                        const point=item.mapToItem(box,0,0);
                        const overflow=Math.max(-point.x,-point.y,point.x+item.width-box.width,point.y+item.height-box.height);
                        if(box.width>0 && box.height>0 && overflow>1.5 && (typeof item.value === "number" || typeof item.currentIndex === "number" || (typeof item.clicked === "function" && item.text)))findings.push({kind:"outside-card",type:String(item).split('(')[0],text:item.text ?? "",overflow:Math.round(overflow*10)/10,point:{x:point.x,y:point.y},size:{w:item.width,h:item.height},card:{w:box.width,h:box.height,controlHeight:card.height,type:String(card).split("(")[0]}});
                    }
                    if(typeof item.clicked === "function" && item.contentItem && typeof item.contentItem.text === "string") {
                        const shown=item.contentItem.text;
                        if(!item.text.includes("&&") && /&[^&\s]/.test(shown)) findings.push({kind:"mnemonic-visible",text:shown});
                    }
                    if(typeof item.toolTipText === "string" && item.display===0 && item.width>56)
                        findings.push({kind:"oversized-icon",text:item.text,width:item.width});
                }
                for(const child of item.children ?? [])visit(child);
            }
            visit(base);
            return JSON.stringify({module:root.nState.systemModule,page:root.nState.currentPageIdx,width:root.width,height:root.height,host:{w:systemPage.backend.width,h:systemPage.backend.height,pageH:systemPage.backend.page?.height,pageW:systemPage.backend.page?.width},window:{visible:WindowFactory.openWindow.visible,minimized:WindowFactory.openWindow.minimized,actualVisible:root.Window.window?.visible,visibility:root.Window.window?.visibility},examined:examined,findings:findings});
            } catch(error) {return JSON.stringify({error:String(error),stack:error.stack});}
        }
        function resize(width: int,height: int): void {WindowFactory.openWindow.implicitWidth=width;WindowFactory.openWindow.implicitHeight=height;}
        function vramCard() {
            function find(item) {
                if(item.capacity!==undefined && item.contextTokens!==undefined)return item;
                for(const child of item.children ?? []) {const found=find(child);if(found)return found;}
                return null;
            }
            return find(testPages);
        }
        function vramFacts(): string {
            const item=vramCard();
            if(!item)return "{}";
            return JSON.stringify({ready:item.snapshot!==null,capacity:item.capacity,model:item.modelBytes,context:item.contextBytes,runtime:item.runtimeBytes,remaining:item.remaining,preview:item.showingPreview,cpuOnly:item.local?.cpuOnly,canPreview:item.canPreview,tokens:item.contextTokens,localName:item.local?.name,includeCurrent:item.includeCurrent});
        }
        function vramPreview(enabled: bool,tokens: int): void {
            const item=vramCard();if(item){item.preview=enabled;item.contextTokens=tokens;}
        }
        function hermesFacts(): string {
            const page=testPages.currentItem;
            return JSON.stringify({ready:page?.saved!==null && page?.saved!==undefined,model:page?.selectedModel,thinking:page?.thinking,dirty:page?.dirty,loading:page?.loading,error:page?.failed,chatgptAuth:page?.chatgptAuth,codexLoggedIn:page?.codexLoggedIn});
        }
        function endpointFacts(): string {
            const page=testPages.currentItem;
            let panel=null;let fields=0;
            function find(item) {
                if(item.objectName==="hermesEndpointPanel")panel=item;
                if(item.Accessible.name?.startsWith("Endpoint"))fields++;
                for(const child of item.children ?? [])find(child);
            }
            find(page);
            if(panel)page.flickable.contentY=Math.max(0,panel.mapToItem(page.flickable.contentItem,0,0).y-10);
            return JSON.stringify({panel:panel!==null,fields:fields,model:page.selectedModel,error:page.failed});
        }
        function cloudAccessFacts(): string {
            function find(item,name) {
                if(item.objectName===name)return item;
                for(const child of item.children ?? []) {const found=find(child,name);if(found)return found;}
                return null;
            }
            const access=find(testPages,"hermesCloudAccess");
            const local=find(testPages,"hermesLocalModels");
            return JSON.stringify({height:access?.height,target:access?.targetHeight,localY:local?.mapToItem(root,0,0).y,animations:GlobalConfig.appearance.anim.enabled});
        }
        function controlFacts(): string {
            screenshotTest.grabImage(root);
            const facts={help:[],hdr:null};
            function visit(item){
                if(!item || !item.visible)return;
                if(typeof item.toolTipText === "string" && item.display===0)
                    facts.help.push({width:item.width,implicitWidth:item.implicitWidth});
                if(item.checkable && typeof item.text === "string" && item.text.includes("HDR"))
                    facts.hdr={source:item.text,shown:item.contentItem?.text,checked:item.checked};
                for(const child of item.children ?? [])visit(child);
            }
            visit(systemPage.backend.page);return JSON.stringify(facts);
        }
        function replaceHdrLabel(): bool {
            function find(item){
                if(!item || !item.visible)return null;
                if(item.checkable && typeof item.text === "string" && item.text.includes("HDR"))return item;
                for(const child of item.children ?? []){const found=find(child);if(found)return found;}
                return null;
            }
            const control=find(systemPage.backend.page);if(!control)return false;
            control.contentItem=Qt.createQmlObject('import QtQuick; Text { text: "late &HDR" }',control);
            return true;
        }
        function nativeAction(): bool {
            const action=systemPage.moduleActions.find(a=>a.visible !== false && a.enabled);
            if(!action)return false;action.trigger();return true;
        }
        function nativeBack(): void {systemPage.backend.back();}
        function minimize(): void {WindowFactory.openWindow.minimized=true;}
        function showForCapture(): void {
            WindowFactory.openWindow.visible=true;
            WindowFactory.openWindow.minimized=false;
            const win=Kwin.windowList.find(w=>w.title===WindowFactory.openWindow.title);
            if(win)Kwin.focusWindow(win.address);
        }
        function capture(path: string): bool {const image=screenshotTest.grabImage(root);image.save(path);return true;}
        function restorePreferences(transparency: bool,animations: bool,scale: real,automatic: bool): void {
            GlobalConfig.appearance.transparency.enabled=transparency;
            GlobalConfig.appearance.anim.enabled=animations;
            GlobalConfig.appearance.font.scale=scale;
            GlobalConfig.services.autoSchemeEnabled=automatic;
            GlobalConfig.save();
        }
        function searchNative(label: string): void {
            const entry=PageRegistry.fuzzyEntries(label)[0];
            if(!entry || entry.settingLabel!==label || !entry.systemModule)throw new Error("No native search entry: "+label);
            PageRegistry.activateEntry(root.nState,entry);
        }
        function module(id: string, title: string): void {root.nState.openSystemModule(id,title);}
        function back(): void {root.nState.requestBack();}
        function editMouse(): bool {
            if(root.nState.systemModule!=="kcm_mouse")return false;
            function find(item){
                if(item.checkState !== undefined && item.enabled && item.visible && typeof item.click === "function")return item;
                for(const child of item.children ?? []){const found=find(child);if(found)return found;}
                return null;
            }
            const item=find(systemPage.backend.page);
            if(!item)return false;item.click();return true;
        }
        function decide(label: string): bool {
            function find(item){
                if(item.text===label && typeof item.click === "function")return item;
                for(const child of item.children ?? []){const found=find(child);if(found)return found;}
                return null;
            }
            const item=find(leaveDialog.contentItem);if(!item)return false;item.click();return true;
        }
        function closeWindow(address: string): void { Kwin.closeWindow(address); }
        function search(query: string): void { root.nState.searchQuery=query; }
        function textScale(value: real): void {
            function find(item) {
                if (item.objectName === "flausenTextScale") return item;
                for (const child of item.children ?? []) { const found=find(child); if(found)return found; }
                return null;
            }
            const item=find(root); item.value=value; item.moved();
        }
    }
