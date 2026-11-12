import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../main.js',import.meta.url),'utf8');
class Signal { handlers=[]; connect(fn){this.handlers.push(fn);} emit(...args){for(const fn of this.handlers)fn(...args);} }
function setup(start=0,occupied=[],alreadyFullscreen=false) {
 const desktops=[1,2,3,4].map(id=>({id:String(id)}));
 function window(desktop,extra={}) {
  let assigned=[desktops[desktop]];
  const w={normalWindow:true,fullScreen:false,desktopWindow:false,dock:false,onAllDesktops:false,
   fullScreenChanged:new Signal(),desktopsChanged:new Signal(),transientChanged:new Signal(),...extra};
  Object.defineProperty(w,'desktops',{get:()=>assigned,set:value=>{assigned=value;w.desktopsChanged.emit();}});
  return w;
 }
 const candidate=window(start,{fullScreen:alreadyFullscreen});
 const windows=[candidate,...occupied.map(id=>window(id))];
 const workspace={desktops,currentDesktop:desktops[start],activeWindow:candidate,
  windowList:()=>windows,windowAdded:new Signal(),windowRemoved:new Signal(),
  createDesktop(){throw Error('Must never create a desktop');},removeDesktop(){throw Error('Must never remove a desktop');}};
 const ctx=vm.createContext({workspace,candidate});vm.runInContext(source,ctx);
 return {desktops,candidate,windows,workspace,window,ctx};
}
let count=0;
for(let start=0;start<4;start++) for(let mask=0;mask<16;mask++) {
 const occupied=[0,1,2,3].filter(i=>mask&(1<<i));const fixture=setup(start,occupied);
 const ordered=[1,2,3].map(offset=>(start+offset)%4);
 const expected=ordered.find(i=>!occupied.includes(i))??ordered[0];
 assert.equal(vm.runInContext('destination(candidate).id',fixture.ctx),String(expected+1));count++;
}
{
 const f=setup(0,[1]);const dialog=f.window(0,{normalWindow:false,transientFor:f.candidate});
 f.windows.push(dialog);f.workspace.windowAdded.emit(dialog); // Existing-dialog movement also runs on enter.
 f.candidate.fullScreen=true;f.candidate.fullScreenChanged.emit();
 assert.equal(f.candidate.desktops[0].id,'3');assert.equal(f.workspace.currentDesktop.id,'3');assert.equal(dialog.desktops[0].id,'3');
 f.candidate.fullScreen=false;f.candidate.fullScreenChanged.emit();
 assert.equal(f.candidate.desktops[0].id,'1');assert.equal(dialog.desktops[0].id,'1');assert.equal(f.workspace.currentDesktop.id,'1');
}
{
 const f=setup(3,[0,1,2,3]);f.candidate.fullScreen=true;f.candidate.fullScreenChanged.emit();
 assert.equal(f.candidate.desktops[0].id,'1');
 f.candidate.desktops=[f.desktops[1]];f.candidate.fullScreen=false;f.candidate.fullScreenChanged.emit();
 assert.equal(f.candidate.desktops[0].id,'2');
}
{
 const f=setup(0,[0,1,2,3]);
 f.candidate.fullScreen=true;f.candidate.fullScreenChanged.emit();
 assert.equal(f.candidate.desktops[0].id,'2');
 const app=f.window(1);const ownDialog=f.window(1,{normalWindow:false,transientFor:f.candidate});
 for(const w of [app,ownDialog]) {f.windows.push(w);f.workspace.windowAdded.emit(w);}
 assert.deepEqual(Array.from(app.desktops,d=>d.id),['1']);
 assert.equal(ownDialog.desktops[0].id,'2');
 f.workspace.currentDesktop=f.desktops[0];
 assert.equal(vm.runInContext('destination(workspace.windowList()[1]).id',f.ctx),'3');
}
{
 // A fresh script instance must protect an existing fullscreen without moving it.
 const f=setup(3,[],true);
 assert.equal(f.candidate.desktops[0].id,'4');
 const app=f.window(3);
 f.windows.push(app);f.workspace.windowAdded.emit(app);
 assert.equal(app.desktops[0].id,'3');
}
console.log(`${count} occupancy/start combinations; fullscreen/dialog restoration, manual move and reserved desktops passed.`);
