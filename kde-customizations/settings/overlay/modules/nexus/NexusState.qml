import QtQuick
import Quickshell
import Quickshell.Bluetooth

QtObject {
    property ShellScreen screen
    property bool isWindow
    property bool animatingContainer
    property int currentPageIdx
    property list<int> subPageIdxStack
    property string systemModule: ""
    property string systemTitle: ""
    property var systemHistory: []
    property bool systemDirty: false
    property var pendingAction: null
    signal confirmLeave
    function attempt(action): void {
        if (systemDirty) { pendingAction=action; confirmLeave(); }
        else action();
    }
    function finishPending(): void {
        const action=pendingAction; pendingAction=null; systemDirty=false;
        if(action) action();
    }
    function cancelPending(): void { pendingAction=null; }
    function openSystemModule(module: string, title: string): void {
        attempt(() => {
            if (systemModule) systemHistory.push({module:systemModule,title:systemTitle});
            systemModule=module==="kcm_clock" ? "@clock" : module;
            systemTitle=title;
        });
    }
    function navigateToSystemModule(page: int, module: string, title: string): void {
        attempt(() => {
            systemHistory=[];
            currentPageIdx=page;
            systemModule=module==="kcm_clock" ? "@clock" : module;
            systemTitle=title;
        });
    }
    function backFromSystemModule(): void {
        attempt(() => {
            const previous=systemHistory.pop();
            systemModule=previous?.module ?? "";
            systemTitle=previous?.title ?? "";
        });
    }
    function requestBack(): void {
        if (systemModule) backFromSystemModule();
        else if (subPageIdxStack.length) closeSubPage();
        else requestExit();
    }
    function requestExit(): void { attempt(() => close()); }
    property bool searchOpen
    property string searchQuery

    property string selectedWallpaperCategory
    property string wallpaperFilterType: "all"
    property BluetoothDevice selectedBtDevice
    property DesktopEntry selectedApp
    property int editingVpnIndex: -1
    property string selectedNetworkSsid
    property string selectedNetworkUuid
    property string selectedEthernetInterface
    property bool networkDetailsFromSaved

    property string pendingNetworkSsid: ""

    property int pendingSubPageIdx: -1

    signal close
    signal subPageOpened(idx: int)
    signal subPageClosed

    function openSubPage(idx: int): void {
        subPageIdxStack.push(idx);
        subPageOpened(idx);
    }

    // Navigation that changes page, such as a search result. Landing on the
    // page that is already showing still opens immediately: nothing to wait for.
    function goToSubPage(pageIdx: int, subPageIdx: int): void {
        attempt(() => {
            systemModule="";systemTitle="";systemHistory=[];
            navigateToSubPage(pageIdx,subPageIdx);
        });
    }
    function navigateToSubPage(pageIdx: int, subPageIdx: int): void {
        if (pageIdx === currentPageIdx) {
            pendingSubPageIdx = -1;
            if (subPageIdx >= 0)
                openSubPage(subPageIdx);
            else
                while (subPageIdxStack.length > 0) closeSubPage();
            return;
        }
        currentPageIdx = pageIdx;
        pendingSubPageIdx = subPageIdx;
    }

    function closeSubPage(): void {
        subPageClosed();
        subPageIdxStack.pop();
    }

    function openNetworkDetail(ssid: string, uuid: string, fromSaved: bool): void {
        selectedNetworkSsid = ssid;
        selectedNetworkUuid = uuid;
        networkDetailsFromSaved = fromSaved;
        openSubPage(3);
    }

    onCurrentPageIdxChanged: {
        subPageIdxStack.length = 0;
        pendingSubPageIdx = -1;
    }
}
