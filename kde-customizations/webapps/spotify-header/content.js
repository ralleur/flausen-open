(() => {
    const headerSelector = '[data-testid="global-nav-bar"]';
    let port, controls, grip, style, header, enabled = false, serial = 0, manipulating = false;
    const pending = new Map();
    function request(action, extra = {}) {
        return new Promise((resolve, reject) => {
            const id = ++serial;
            const timer = setTimeout(() => { pending.delete(id); reject(new Error("Window bridge timeout")); }, 4000);
            pending.set(id, {resolve, reject, timer});
            port.postMessage({id, action, ...extra});
        });
    }
    function cleanup() {
        enabled = false;
        controls?.remove(); grip?.remove(); style?.remove();
        header?.removeAttribute("data-flausen-header");
        document.documentElement.removeAttribute("data-flausen-window");
        for (const item of pending.values()) { clearTimeout(item.timer); item.reject(new Error("Disconnected")); }
        pending.clear();
    }
    const paths = {
        minimize: '<path d="M4 11.5h8"/>',
        maximize: '<rect x="4.5" y="4.5" width="7" height="7"/>',
        close: '<path d="m4.5 4.5 7 7m0-7-7 7"/>'
    };
    function action(name) { request(name).catch(error => console.warn("flausen Spotify:", error.message)); }
    async function start() {
        header = document.querySelector(headerSelector);
        if (!header || port) return;
        observer.disconnect();
        port = chrome.runtime.connect({name: "spotify-header"});
        port.onDisconnect.addListener(cleanup);
        port.onMessage.addListener(message => {
            const item = pending.get(message.id);
            if (!item) return;
            pending.delete(message.id); clearTimeout(item.timer);
            if (message.error) item.reject(new Error(message.error)); else item.resolve(message);
        });
        const title = document.title;
        const token = "flausen-spotify-" + crypto.randomUUID();
        try {
            // Match this exact native window, including when several Spotify windows exist.
            document.title = token;
            for (let attempt = 0; ; attempt++) {
                try { await request("identify", {token}); break; }
                catch (error) {
                    if (attempt >= 9 || !error.message.includes("not identified")) throw error;
                    await new Promise(resolve => setTimeout(resolve, 100));
                    document.title = token;
                }
            }
        } catch (error) {
            console.warn("flausen Spotify:", error.message);
            port.disconnect(); cleanup(); return;
        } finally {
            if (document.title === token) document.title = title;
        }
        style = document.createElement("style");
        style.textContent = `
          [data-flausen-header] { padding-right: 119px !important; position: relative !important; }
          #flausen-window-controls { position: absolute; right: 5px; top: 50%; transform: translateY(-50%);
            display: flex; gap: 6px; z-index: 100; color: #fff; }
          #flausen-window-controls button { all: unset; box-sizing: border-box; width: 30px; height: 30px;
            display: grid; place-items: center; border-radius: 4px; color: inherit; cursor: default; }
          #flausen-window-controls button:hover { background: #ffffff1f; }
          #flausen-window-controls button:active { background: #ffffff33; }
          #flausen-window-controls button:focus-visible { outline: 2px solid currentColor; outline-offset: -2px; }
          #flausen-window-controls svg { width: 16px; height: 16px; fill: none; stroke: currentColor;
            stroke-width: 1.2; stroke-linecap: square; pointer-events: none; }
          html[data-flausen-window="inactive"] #flausen-window-controls { color: #ffffff8c; }
          #flausen-window-resize { position: fixed; right: 0; bottom: 0; width: 10px; height: 10px;
            z-index: 2147483646; cursor: nwse-resize; }
          :fullscreen #flausen-window-resize { display: none; }
        `;
        document.head.append(style);
        controls = document.createElement("div");
        controls.id = "flausen-window-controls";
        controls.setAttribute("role", "group");
        controls.setAttribute("aria-label", "Fenstersteuerung");
        for (const [name, label] of [["minimize", "Minimieren"], ["maximize", "Maximieren / Wiederherstellen"], ["close", "Schließen"]]) {
            const button = document.createElement("button");
            button.type = "button"; button.title = label; button.setAttribute("aria-label", label);
            button.innerHTML = `<svg viewBox="0 0 16 16" aria-hidden="true">${paths[name]}</svg>`;
            button.addEventListener("click", event => { if (event.isTrusted) action(name); });
            controls.append(button);
        }
        header.setAttribute("data-flausen-header", "");
        header.append(controls);
        grip = document.createElement("div");
        grip.id = "flausen-window-resize";
        grip.setAttribute("aria-hidden", "true");
        grip.addEventListener("pointerdown", event => {
            if (enabled && event.isTrusted && event.button === 0) {
                event.preventDefault(); grip.setPointerCapture(event.pointerId);
                manipulating = true; action("resize");
            }
        });
        document.body.append(grip);
        try { await request("enable"); enabled = true; }
        catch (error) { port.disconnect(); cleanup(); return; }
        const focus = () => document.documentElement.setAttribute("data-flausen-window", document.hasFocus() ? "active" : "inactive");
        focus(); window.addEventListener("focus", focus); window.addEventListener("blur", focus);
        const interactive = 'button, a, input, label, [role="button"], [role="search"], [contenteditable="true"]';
        let drag = null;
        header.addEventListener("pointerdown", event => {
            if (!enabled || !event.isTrusted || event.button !== 0 || event.target.closest(interactive)) return;
            event.preventDefault();
            header.setPointerCapture(event.pointerId);
            drag = {x: event.clientX, y: event.clientY};
        });
        header.addEventListener("pointermove", event => {
            if (!enabled || !event.isTrusted || !drag) return;
            if (!(event.buttons & 1)) { drag = null; return; }
            if (Math.hypot(event.clientX - drag.x, event.clientY - drag.y) > 4) {
                drag = null; manipulating = true; action("move");
            }
        });
        const end = () => {
            drag = null;
            if (manipulating) { manipulating = false; action("end"); }
        };
        window.addEventListener("pointerup", end);
        window.addEventListener("pointercancel", end);
        window.addEventListener("blur", end);
        header.addEventListener("dblclick", event => {
            if (enabled && event.isTrusted && event.button === 0 && !event.target.closest(interactive)) action("maximize");
        });
        // Spotify is a SPA; drop back to native controls if its header disappears.
        new MutationObserver(() => {
            if (enabled && (!header.isConnected || !controls.isConnected)) { port.disconnect(); cleanup(); }
        }).observe(document.body, {childList: true, subtree: true});
        window.addEventListener("pagehide", () => port.disconnect(), {once: true});
    }
    const observer = new MutationObserver(start);
    observer.observe(document.body, {childList: true, subtree: true});
    start();
})();
