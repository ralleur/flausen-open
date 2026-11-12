#!/usr/bin/env python3
"""Native previews with fabricated clipboard/images and a no-op recorder."""
from pathlib import Path
import os,tempfile,shutil,subprocess,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=['capture','clipboard'],required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--expanded',action='store_true');parser.add_argument('--record',action='store_true');parser.add_argument('--running',action='store_true');parser.add_argument('--paused',action='store_true');parser.add_argument('--copy',action='store_true');parser.add_argument('--action',choices=['ocr','search']);parser.add_argument('--selected',action='store_true');parser.add_argument('--empty',action='store_true');parser.add_argument('--font-scale',type=float,default=1.15);args=parser.parse_args();args.out=args.out.resolve();args.out.parent.mkdir(parents=True,exist_ok=True)
source=Path.home()/'.config/quickshell/caelestia'
with tempfile.TemporaryDirectory(prefix='capture-clipboard-preview-') as folder:
 root=Path(folder)
 for p in source.iterdir():
  if p.name not in ['modules','shell.qml']:(root/p.name).symlink_to(p,target_is_directory=p.is_dir())
 (root/'modules/bar').mkdir(parents=True)
 for p in (source/'modules').iterdir():
  if p.name!='bar':(root/'modules'/p.name).symlink_to(p,target_is_directory=p.is_dir())
 for p in (source/'modules/bar').iterdir():
  if p.name!='popouts':(root/'modules/bar'/p.name).symlink_to(p,target_is_directory=p.is_dir())
 shutil.copytree(source/'modules/bar/popouts',root/'modules/bar/popouts')
 popouts=root/'modules/bar/popouts';fake=root/'preview';fake.mkdir();(root/'shots').mkdir();(root/'recordings').mkdir()
 # Action checks use local command shims: no clipboard change, upload or browser.
 shims=root/'shims';shims.mkdir()
 for command,script in {
  'cp':'printf \"%s\" \"$3\" > \"'+str(root/'temporary.txt')+'\"; exec /usr/bin/cp \"$@\"',
  'wl-copy':'cat > "'+str(root/'copied.txt')+'"',
  'notify-send':'exit 0',
  'xdg-open':'printf "%s" "$1" > "'+str(root/'opened.txt')+'"',
  'curl':'printf \'%s\' \'{"files":[{"url":"https://example.test/capture.png"}]}\'',
  'tesseract':'if [ "$1" = "--list-langs" ]; then printf "Languages\\neng\\n"; else printf "Fixture text"; fi',
 }.items():
  executable=shims/command;executable.write_text('#!/bin/sh\n'+script+'\n');executable.chmod(0o755)
 image=root/'example.png'
 from PIL import Image,ImageDraw
 sample=Image.new('RGB',(480,270),'#192b3c');draw=ImageDraw.Draw(sample);draw.rectangle((25,25,455,245),outline='#287dff',width=4);draw.text((160,125),'Vorschaubeispiel',fill='white');sample.save(image)
 if not args.empty:
  for i in range(6):
   target=root/'shots'/f'screenshot-2026-11-02_12.0{i}.00.png'
   shutil.copy2(image,target);os.utime(target,(1793617200+i*60,1793617200+i*60))
 p=popouts/'MenuScreenshotList.qml';s=p.read_text().replace('id: root', 'id: root\n    property bool fixtureActionStarted: false',1).replace('GlobalConfig.paths.screenshotsDir',json.dumps(str(root/'shots')));s=s.replace('id: pointer', 'id: pointer\n                    objectName: "fixtureShotPointer"');p.write_text(s)
 p=popouts/'MenuRecordingList.qml';p.write_text(p.read_text().replace('GlobalConfig.paths.recordingsDir',json.dumps(str(root/'recordings'))))
 p=popouts/'MenuCaptureCard.qml';p.write_text(p.read_text().replace('import qs.services','import qs.preview as Fixtures\nimport qs.services').replace('Recorder.','Fixtures.Recorder.'))
 p=popouts/'ClipboardHistory.qml';p.write_text(p.read_text().replace('import qs.modules.launcher.services as Launcher','import qs.preview as Launcher'))
 (fake/'qmldir').write_text('module qs.preview\nsingleton Clipboard 1.0 Clipboard.qml\nsingleton Recorder 1.0 Recorder.qml\n')
 (fake/'Recorder.qml').write_text('''pragma Singleton
import QtQuick
import Quickshell
QtObject {
 property bool running:Quickshell.env("FIXTURE_RUNNING")==="1"
 property bool paused:Quickshell.env("FIXTURE_PAUSED")==="1"
 property int elapsed:0
 function start(options) {} function startGif() {} function stop() {} function togglePause() {} function launchSpectacle() {}
}
''')
 entries=[] if args.empty else [dict(id=1,isImage=False,isPinned=False,preview='Ein kurzer Beispieltext'),dict(id=2,isImage=False,isPinned=True,pinId='example',preview='Angehefteter Eintrag mit längerer Beschriftung und einer zweiten Zeile für die Vorschau.'),dict(id=3,isImage=True,isPinned=False,preview='Image')]
 (fake/'Clipboard.qml').write_text('''pragma Singleton
import QtQuick
QtObject {
 property bool available:true
 signal imageReady(int id,string path)
 function reload() {} function pin(id) {} function unpin(id) {} function copyPinned(id) {}
 function getSortedItems() {return '''+json.dumps(entries,ensure_ascii=False)+''';}
 function isImageCached(id) {return true;}
 function getImagePath(id) {return '''+json.dumps(str(image))+''';}
}
''')
 (root/'shell.qml').write_text('''import QtQuick
import QtQuick.Window
import Quickshell
import Caelestia
import Caelestia.Config
import qs.components
import qs.modules.bar.popouts as Popouts
import qs.services
ShellRoot {
 Binding {target:Translations;property:"extraSearchPaths";value:[Qt.resolvedUrl("translations")]}
 Binding {target:Translations;property:"language";value:GlobalConfig.general.language}
 Window {
  id:window;property bool fixtureClicked:false;visible:true;width:1000;height:1000;color:"#11161d"
  DrawerVisibilities {id:fixtureVisibilities}
  Popouts.PopoutState {id:state}
  Rectangle {
   id:surface;x:20;y:20;width:SURFACE_WIDTH;height:loader.implicitHeight+38;radius:28;color:MenuStyle.taskbarSurface;border.width:1;border.color:MenuStyle.border
   Loader {id:loader;x:(parent.width-width)/2;y:19;width:CONTENT_WIDTH;sourceComponent:Quickshell.env("FIXTURE_KIND")==="clipboard" ? clipboard : capture}
   Component {id:clipboard;Popouts.ClipboardHistory {popouts:state;scaleOffset:1.15;fontScale:FONT_SCALE}}
   Component {id:capture;Popouts.ScreenCapture {popouts:state;visibilities:fixtureVisibilities;scaleOffset:1.15;fontScale:FONT_SCALE}}
  }
  Timer {interval:250;running:true;onTriggered:{
   function prepare(item) {
    if(Quickshell.env("FIXTURE_COPY")==="1" && item.objectName==="fixtureShotPointer" && !window.fixtureClicked) {
      window.fixtureClicked=true;
      item.clicked(null);
    }
    if((Quickshell.env("FIXTURE_SELECTED")==="1" || Quickshell.env("FIXTURE_ACTION")) && item.selectedPath!==undefined) {
      item.selectedPath=item.shotsdir+"/screenshot-2026-11-02_12.05.00.png";
      item.selectedSize=Qt.size(480,270);
      if(Quickshell.env("FIXTURE_ACTION") && !item.fixtureActionStarted) {
        item.fixtureActionStarted=true;
        item.actOnSelection(Quickshell.env("FIXTURE_ACTION")==="ocr" ? 3 : 2);
      }
    }
    if(item.props!==undefined && item.shotMode!==undefined)item.props.captureMode=Quickshell.env("FIXTURE_RECORD")==="1" ? "record" : "shot";
    if(Quickshell.env("FIXTURE_EXPANDED")==="1" && item.menu!==undefined && item.expanded!==undefined && item.visible)item.expanded=true;
    for(const child of item.children ?? [])prepare(child);
    if(item.item)prepare(item.item);
   } prepare(loader.item);
  }}
  Timer {interval:1700;running:true;onTriggered:{
   const rows=[];
   function visit(item){
    if(item.font!==undefined && item.text!==undefined && item.visible)rows.push({text:item.text,font:item.font.family,size:item.font.pointSize});
    for(const child of item.children ?? [])visit(child);
    if(item.item)visit(item.item);
   }visit(loader.item);
   const target=Quickshell.env("FIXTURE_EXPANDED")==="1" ? window.contentItem : surface;
   target.grabToImage(result=>{console.log("CAPTURE_CLIPBOARD_PREVIEW",JSON.stringify({saved:result.saveToFile(Quickshell.env("FIXTURE_OUT")),width:surface.width,height:surface.height,rows:rows}));Qt.quit();});
  }}
  Timer {interval:10000;running:true;onTriggered:Qt.quit()}
 }
}
'''.replace('FONT_SCALE',str(args.font_scale)).replace('SURFACE_WIDTH', '681' if args.kind == 'capture' else '520').replace('CONTENT_WIDTH', '644' if args.kind == 'capture' else '483'))
 env=dict(os.environ,PATH=str(shims)+os.pathsep+os.environ["PATH"],FIXTURE_COPY="1" if args.copy else "0",FIXTURE_RUNNING="1" if args.running else "0",FIXTURE_PAUSED="1" if args.paused else "0",FIXTURE_ACTION=args.action or "",QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+folder,QS_NO_RELOAD_POPUP='1',QS_DISABLE_CRASH_HANDLER='1',FIXTURE_SELECTED='1' if args.selected else '0',FIXTURE_KIND=args.kind,FIXTURE_OUT=str(args.out),FIXTURE_RECORD='1' if args.record else '0',FIXTURE_EXPANDED='1' if args.expanded else '0')
 result=subprocess.run(['quickshell','-p',folder],env=env,capture_output=True,text=True,timeout=15)
 lines=(result.stdout+result.stderr).splitlines();facts=next((json.loads(line.split('CAPTURE_CLIPBOARD_PREVIEW ',1)[1]) for line in lines if 'CAPTURE_CLIPBOARD_PREVIEW ' in line),None)
 errors=[line for line in lines if any(token in line for token in ['ReferenceError','TypeError','Error:', 'Binding loop','Unable to assign [undefined]'])]
 if not facts or not facts['saved'] or errors:raise RuntimeError('\n'.join(errors or lines[-25:]))
 if args.kind == 'capture':
  texts=[row['text'] for row in facts['rows']]
  assert 'Copy' not in texts, 'Redundant Copy button remains'
  if args.running and not args.record:
   assert 'Recent captures' in texts or 'Image copied' in texts, 'Screenshot gallery hidden during recording'
   assert 'REC' not in texts and 'PAUSED' not in texts, 'Recording info leaked into screenshot mode'
  if args.running and args.record:
   assert ('PAUSED' if args.paused else 'REC') in texts, 'Recording controls missing'
 if args.copy:
  assert (root/'copied.txt').read_bytes()==image.read_bytes(), 'Clicked image was not copied in full'
  assert 'Image copied' in [row['text'] for row in facts['rows']], 'Copy feedback missing'
  facts['copyCheck']={'clickedImageCopied':True,'externalCommands':'isolated shims'}
 if args.action:
  assert (root/'shots/screenshot-2026-11-02_12.05.00.png').read_bytes()==image.read_bytes(), 'Original image changed'
  expected='Fixture text' if args.action=='ocr' else 'https://lens.google.com/uploadbyurl?url=https://example.test/capture.png'
  artifact=root/('copied.txt' if args.action=='ocr' else 'opened.txt')
  assert artifact.read_text()==expected, 'Unexpected action result'
  assert not Path((root/'temporary.txt').read_text()).exists(), 'Temporary image was not removed'
  facts['actionCheck']={'action':args.action,'originalPreserved':True,'temporaryRemoved':True,'result':artifact.read_text(),'externalCommands':'isolated shims'}
 args.out.with_suffix('.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({key:value for key,value in facts.items() if key!='rows'}))
