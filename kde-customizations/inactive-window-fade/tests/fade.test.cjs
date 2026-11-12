const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
function setup(duration = 250) {
    let now = 0;
    const animations = [], cancelled = [];
    const signal = {connect() {}};
    const context = vm.createContext({
        Date: {now: () => now},
        effects: {stackingOrder: [], windowAdded: signal, windowClosed: signal},
        effect: {readConfig: () => false}, Effect: {Opacity: 0}, QEasingCurve: {InOutCubic: 3},
        animationTime: () => duration,
        animate: options => {animations.push(options); return [animations.length];},
        cancel: ids => cancelled.push(ids),
    });
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../contents/code/main.js'), 'utf8'), context);
    return {context, animations, cancelled, tick: value => now = value};
}
test('both focus directions preserve the previous painted opacity at the first frame', () => {
    const s = setup(), w = {normalWindow: true};
    for (const [old, next] of [[1, .95], [.95, 1]]) {
        s.context.changed(w, old, next);
        const a = s.animations.at(-1);
        assert.ok(Math.abs(a.from * next - old) < 1e-10);
        assert.equal(a.to * next, next);
        s.tick(1000);
    }
});
test('rapid focus reversal continues from the intermediate painted opacity', () => {
    const s = setup(), w = {normalWindow: true};
    s.context.changed(w, 1, .95);
    s.tick(125);
    s.context.changed(w, .95, 1);
    assert.ok(Math.abs(s.animations[1].from - .975) < 1e-10);
    assert.equal(s.cancelled.length, 1);
    s.context.clear(w);
    assert.equal(s.cancelled.length, 2);
});
test('exceptions, hidden bridges, popups and unrelated opacity changes stay untouched', () => {
    const s = setup();
    for (const [w, old, next] of [
        [{dialog: true}, 1, 1], [{normalWindow: true}, 0, 1],
        [{normalWindow: true}, .8, 1], [{popup: true}, 1, .95],
        [{normalWindow: true, deleted: true}, 1, .95],
        [{normalWindow: true, minimized: true}, 1, .95],
    ]) s.context.changed(w, old, next);
    assert.equal(s.animations.length, 0);
    s.context.changed({dialog: true}, 1, .95);
    assert.equal(s.animations.length, 1);
});
test('disabled system animations do not create compensation', () => {
    const s = setup(0);
    s.context.changed({normalWindow: true}, 1, .95);
    assert.equal(s.animations.length, 0);
});
test('fast global animations retain a perceptible fade, slower settings are respected', () => {
    for (const duration of [62, 500]) {
        const s = setup(duration);
        s.context.changed({normalWindow: true}, 1, .95);
        assert.equal(s.animations[0].duration, Math.max(250, duration));
    }
});
