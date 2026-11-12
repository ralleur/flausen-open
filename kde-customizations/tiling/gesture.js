// Installed inside Krohnkite's script.js; uses its window state and layout engine.
var RALLEUR_INPUT = null;

function ralleurMoveStart(controller, ctx, window) {
    window.ralleurTileDrop = RALLEUR_INPUT.tileGesture();
    if (window.isFloating) window.ralleurFloatGeometry = window.actualGeometry.clone();
    window.isDragging = true;
    if (!window.ralleurTileDrop && window.isTiled) {
        const before = window.actualGeometry.clone();
        const saved = (window.ralleurFloatGeometry || window.floatGeometry).clone();
        const point = ctx.cursorPosition || before.center;
        const rx = clip((point.x - before.x) / before.width, 0, 1);
        const ry = clip((point.y - before.y) / before.height, 0, 1);
        saved.x = point.x - rx * saved.width;
        saved.y = point.y - ry * saved.height;
        window.state = WindowState.Floating;
        window.floatGeometry = saved;
        window.shouldCommitFloat = false;
        // KWin uses a normalized pointer offset, so resizing keeps the grip point.
        window.window.commit(ctx, saved, false, CONFIG.floatedWindowsLayer);
        controller.engine.arrange(ctx, "ralleur-detach", "ralleurMoveStart");
    }
    ralleurMoveStep(controller, ctx, window);
}

// One plan is used by both the preview and the actual drop.
function ralleurDropPlan(controller, ctx, window) {
    const store = controller.engine.windows;
    const point = ctx.cursorPosition || window.actualGeometry.center;
    const tiles = store.getVisibleTiles(window.surface).filter(tile => tile !== window);
    const target = tiles.find(tile => tile.actualGeometry.includesPoint(point));
    const order = store.list.slice();
    const sourceIndex = order.indexOf(window);
    const targetIndex = order.indexOf(target);
    const wasTiled = window.isTiled;
    if (targetIndex >= 0 && sourceIndex >= 0) {
        if (wasTiled) {
            order[sourceIndex] = target;
            order[targetIndex] = window;
        } else {
            // Match WindowStore.move's ordering, including its original index.
            order.splice(sourceIndex, 1);
            order.splice(targetIndex + 1, 0, window);
        }
    }
    const members = order.filter(tile => tile.visible(window.surface) && (tile === window || tile.isTileable));
    const layout = controller.engine.layouts.getCurrentLayout(window.surface);
    const full = !wasTiled && layout.capacity !== null && layout.capacity !== undefined && tiles.length >= layout.capacity;
    if (full) return { full: true, target: null, rects: [], selected: -1 };
    if (!(layout instanceof QuarterLayout)) return null;
    const previewLayout = layout.clone();
    const fake = members.map(tile => ({ state: tile.state, geometry: null }));
    const gaps = controller.engine.getGaps(window.surface);
    const sole = CONFIG.soleWindowOutputOverride[window.surface.output.name] || CONFIG.soleWindowDefaultProps;
    let area = window.surface.workingArea.clone();
    if (fake.length === 1 && (sole.width < 100 || sole.height < 100)) {
        const gx = area.width * (1 - sole.width / 100) / 2;
        const gy = area.height * (1 - sole.height / 100) / 2;
        area = area.gap(gx, gx, gy, gy);
    } else if (!(fake.length === 1 && sole.noGaps)) {
        area = area.gap(gaps.left, gaps.right, gaps.top, gaps.bottom);
    }
    previewLayout.apply(null, fake, area, gaps.between);
    const selected = members.indexOf(window);
    const rects = fake.map((tile, i) => members[i].window.adjustGeometry(tile.geometry).clone());
    return { full: false, target, wasTiled, members, rects, selected };
}

function ralleurMoveStep(controller, ctx, window) {
    if (RALLEUR_INPUT.tileGesture()) window.ralleurTileDrop = true;
    if (!window.ralleurTileDrop) {
        ralleurPreview.hide();
        return;
    }
    const plan = ralleurDropPlan(controller, ctx, window);
    if (!plan) { ralleurPreview.hide(); return; }
    const label = plan.full ? "Tiling voll · 4 Plätze belegt" :
        (plan.wasTiled && plan.target ? "Platz tauschen" : "Hier einordnen");
    ralleurPreview.showPlan(toRect(window.surface.output.geometry), plan.rects, plan.selected, label);
}

function ralleurMoveOver(controller, ctx, window) {
    const tileDrop = window.ralleurTileDrop === true;
    const plan = tileDrop ? ralleurDropPlan(controller, ctx, window) : null;
    window.ralleurTileDrop = false;
    ralleurPreview.hide();
    ctx.setTimeout(() => {
        if (!window.isAlive()) return;
        window.isDragging = false;
        if (!tileDrop || (plan && plan.full)) {
            if (window.isFloating) window.floatGeometry = window.actualGeometry.clone();
            controller.engine.arrange(ctx, "ralleur-free-move", "ralleurMoveOver");
            return;
        }
        const client = window.window.window;
        client.tile = null;
        if (window.isFloating && !window.ralleurFloatGeometry)
            window.ralleurFloatGeometry = window.actualGeometry.clone();
        window.state = WindowState.Tiled;
        if (plan && plan.target && plan.target.isAlive()) {
            if (plan.wasTiled) controller.engine.windows.swap(window, plan.target);
            else controller.engine.windows.move(window, plan.target, true);
        }
        controller.engine.arrange(ctx, "ralleur-tile-drop", "ralleurMoveOver");
    }, 0);
}

function ralleurRestoreCheckpoint(ctx, data) {
    if (!data) return;
    const store = ctx.engine.windows;
    const byId = new Map(store.list.map(w => [w.id, w]));
    const ordered = [];
    for (const record of data.windows) {
        const w = byId.get(record.id);
        if (!w) continue;
        const r = record.floatGeometry;
        if (r) w.ralleurFloatGeometry = new Rect(r.x, r.y, r.width, r.height);
        if (record.tiled) w.state = WindowState.Tiled;
        ordered.push(w);
        byId.delete(record.id);
    }
    store.list = ordered.concat(Array.from(byId.values()));
    for (const record of data.layouts) {
        const w = store.list.find(w => w.id === record.windowId);
        if (!w) continue;
        const layout = ctx.engine.layouts.getCurrentLayout(w.surface);
        if (layout instanceof QuarterLayout) {
            layout.vsplit = record.vsplit;
            layout.lhsplit = record.lhsplit;
            layout.rhsplit = record.rhsplit;
        }
    }
    ctx.engine.arrange(ctx, "ralleur-restore", "ralleurRestoreCheckpoint");
}
