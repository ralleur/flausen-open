// One native connection per document. Losing the document restores its frame.
chrome.runtime.onConnect.addListener(port => {
    if (port.name !== "spotify-header" || port.sender?.frameId !== 0 ||
        port.sender?.origin !== "https://open.spotify.com") {
        port.disconnect();
        return;
    }
    const native = chrome.runtime.connectNative("org.flausen.spotify_header");
    const actions = new Set(["identify", "enable", "move", "resize", "end", "state"]);
    port.onMessage.addListener(message => {
        if (actions.has(message.action)) native.postMessage(message);
        else if (["minimize", "maximize", "close"].includes(message.action)) {
            const id = port.sender.tab.windowId;
            (async () => {
                if (message.action === "close") await chrome.windows.remove(id);
                else if (message.action === "minimize") await chrome.windows.update(id, {state: "minimized"});
                else {
                    const win = await chrome.windows.get(id);
                    await chrome.windows.update(id, {state: win.state === "maximized" ? "normal" : "maximized"});
                }
                port.postMessage({id: message.id, ok: true});
            })().catch(error => port.postMessage({id: message.id, error: error.message}));
        } else port.postMessage({id: message.id, error: "Unsupported window action"});
    });
    native.onMessage.addListener(message => port.postMessage(message));
    native.onDisconnect.addListener(() => {
        // Read lastError so Chromium does not emit an unchecked-runtime warning.
        const error = chrome.runtime.lastError?.message || "Window bridge disconnected";
        try { port.postMessage({error}); port.disconnect(); } catch (_) {}
    });
    port.onDisconnect.addListener(() => native.disconnect());
});
