// Runs Krohnkite's actual controller, engine and QuarterLayout without KWin.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
vm.runInNewContext(source + `
CONFIG = {adjustLayout:true, adjustLayoutLive:true, quarterLayoutReset:false};
const area = new Rect(0, 0, 2000, 1000);
const surface = {id:'test',workingArea:area};
const pending = [];
const ctx = {setTimeout: fn => pending.push(fn)};
const layout = new QuarterLayout();
let requested, commits = 0;
RALLEUR_INPUT = {requestedGeometry: () => requested};
const tiles = [0,1,2,3].map(() => ({
    state:WindowState.Tiled, isTiled:true, surface, ralleurResizePending:false,
    isAlive:()=>true, window:{window:{resize:false}},
    commit:()=>commits++,
    get actualGeometry(){return this.actual;},
    get geometryDelta(){return RectDelta.fromRects(this.geometry, this.actual);}
}));
const engine = Object.create(TilingEngine.prototype);
engine.layouts = {getCurrentLayout:()=>layout};
engine.windows = {getVisibleTiles:()=>tiles};
engine.getGaps = () => ({left:0,right:0,top:0,bottom:0,between:8});
engine.arrange = () => layout.apply(null, tiles, area, 8);
const controller = Object.create(TilingController.prototype);
controller.engine = engine;
const reset = () => {
    layout.resetSplits();engine.arrange();
    for (const w of tiles) {w.actual=w.geometry.clone();w.window.window.resize=false;}
};
const drain = () => {while(pending.length) pending.shift()();};
reset();
const w = tiles[1];
// An older client acknowledgement must not pull the shared edge backwards.
controller.onWindowResizeStart(w, ctx);w.window.window.resize=true;
requested = new Rect(1154,0,846,496);
ralleurResizeStep(controller,ctx,w,requested);
assert.equal(tiles[0].geometry.width,1146);
const split = layout.vsplit;
w.actual = new Rect(1104,0,896,496);
controller.onWindowResize(ctx,w,'buffer');
assert.equal(layout.vsplit,split);
// Repeated acknowledgements and a stationary mouse cannot accumulate drift.
for(let i=0;i<20;i++) {
    ralleurResizeStep(controller,ctx,w,requested);
    controller.onWindowResize(ctx,w,'buffer');
    assert.equal(layout.vsplit,split);
}
// Release arrives while the last buffer is still behind the pointer.
w.window.window.resize=false;
controller.onWindowResizeOver(ctx,w,'finish');drain();
assert.equal(layout.vsplit,split);
assert.equal(w.ralleurResizePending,false);
// Suppress correction timers queued before the drag, for neighbouring tiles too.
reset();const neighbor=tiles[0];neighbor.actual=new Rect(0,0,900,496);
engine.enforceSize(ctx,neighbor);assert.equal(pending.length,1);
controller.onWindowResizeStart(w,ctx);drain();assert.equal(commits,0);
engine.enforceSize(ctx,neighbor);assert.equal(pending.length,0);
// Escape restores the initial requested geometry after moveResizedChanged.
requested=w.geometry.clone();
ralleurResizeStep(controller,ctx,w,new Rect(1204,0,796,496));
controller.onWindowResizeOver(ctx,w,'cancel');drain();
assert.equal(layout.vsplit,0.5);
// Vertical split and clamping retain QuarterLayout's bounds.
reset();controller.onWindowResizeStart(w,ctx);
ralleurResizeStep(controller,ctx,w,new Rect(1004,0,996,646));
assert.equal(layout.rhsplit,0.65);
ralleurResizeStep(controller,ctx,w,new Rect(1904,0,96,996));
assert.equal(layout.vsplit,0.8);assert.equal(layout.rhsplit,0.8);
requested=w.geometry.clone();controller.onWindowResizeOver(ctx,w,'finish');drain();
// With live adjustment disabled, apply the final intent once at release.
reset();CONFIG.adjustLayoutLive=false;controller.onWindowResizeStart(w,ctx);
requested=new Rect(1204,0,796,496);
ralleurResizeStep(controller,ctx,w,requested);assert.equal(layout.vsplit,0.5);
controller.onWindowResizeOver(ctx,w,'finish');drain();assert.equal(layout.vsplit,0.6);
// Floating resize stays outside this path.
const floating={isTiled:false};controller.onWindowResizeStart(floating,ctx);
assert.equal(floating.ralleurResizePending,undefined);
assert.equal(ralleurResizeOver(controller,ctx,floating),false);
`, {assert, console}, {timeout:5000});
console.log('PASS: asynchronous buffers, release, cancellation, correction timers, split bounds, floating');
