#!/usr/bin/env python3
"""Native fixture preview of the taskbar Media layout; no real player is controlled."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--art',type=Path)
p.add_argument('--empty',action='store_true')
p.add_argument('--long',action='store_true')
p.add_argument('--font-scale',type=float,default=1.15)
p.add_argument('--light',action='store_true')
a=p.parse_args();a.out=a.out.resolve();a.out.parent.mkdir(parents=True,exist_ok=True)
shell=Path.home()/'.config/quickshell/caelestia'
with tempfile.TemporaryDirectory(prefix='media-preview-') as tmp:
 root=Path(tmp)
 # Reuse installed dependencies, replacing only player/audio services with fixtures.
 for entry in shell.iterdir():
  if entry.name == 'components':shutil.copytree(entry,root/entry.name)
  elif entry.name not in ['shell.qml','services','modules']:(root/entry.name).symlink_to(entry)
 for directory in ['services','modules']:
  (root/directory).mkdir()
  for entry in (shell/directory).iterdir():
   if (directory,entry.name) not in [('services','Players.qml'),('services','Audio.qml'),('modules','bar')]:
    target=root/directory/entry.name
    if directory == 'services' and entry.is_file():shutil.copy2(entry,target)
    else:target.symlink_to(entry)
 (root/'modules/bar/popouts').mkdir(parents=True)
 (root/'modules/bar/components').symlink_to(shell/'modules/bar/components')
 media=(Path(__file__).resolve().parents[1]/'Media.qml').read_text().replace('readonly property MprisPlayer player:', 'readonly property var player:').replace('required property MprisPlayer modelData','required property var modelData')
 (root/'modules/bar/popouts/Media.qml').write_text(media)
 title='Ein sehr langer Musiktitel für die Prüfung von Zeilenumbruch und stabilen Bedienelementen' if a.long else 'You & Me'
 (root/'services/Audio.qml').write_text('''pragma Singleton
import QtQuick
QtObject { property var appStreams: []; property real volume: 0.5 }
''')
 (root/'services/Players.qml').write_text('''pragma Singleton
import QtQuick
import Quickshell.Services.Mpris
QtObject {
 id: service
 property QtObject fixture: QtObject {
  property string trackTitle: TITLE
  property string trackArtist: "MEUTE"
  property string trackAlbum: "JUBEL"
  property string desktopEntry: "chromium"
  property real position: 102
  property real length: 255
  property bool positionSupported: true
  property bool canSeek: true
  property bool isPlaying: false
  property bool canTogglePlaying: true
  property bool canGoPrevious: true
  property bool canGoNext: true
  property bool shuffleSupported: true
  property bool shuffle: false
  property bool loopSupported: true
  property int loopState: MprisLoopState.None
  property int nextCount: 0
  property int previousCount: 0
  function togglePlaying() { isPlaying = !isPlaying; }
  function next() { nextCount++; }
  function previous() { previousCount++; }
 }
 property QtObject alternative: QtObject {
  property string name: "Second player"
  property string trackTitle: ""
  property string trackArtist: ""
  property string desktopEntry: "chromium"
 }
 property var list: EMPTY ? [] : [fixture, alternative]
 property var manualActive: null
 function sourcePlayer(ignored) { return EMPTY ? null : fixture; }
 function getIdentity(player) { return player === fixture ? "Chromium" : player ? "Second player" : ""; }
 function getArtUrl(player) {
  if (player === alternative) return "file:///matching-cover.png";
  if (player === fixture && !fixture.trackArtist && !fixture.trackAlbum) return "file:///browser-logo.png";
  return player ? ART : "";
 }
 function playerStream(player,audio) { return null; }
 function setPlayerVolume(player,stream,audio,value) { audio.volume = Math.max(0,Math.min(1,value)); }
}'''.replace('TITLE',json.dumps(title)).replace('EMPTY',str(a.empty).lower()).replace('ART',json.dumps(a.art.resolve().as_uri() if a.art else '')))
 (root/'shell.qml').write_text('''import QtQuick
import QtQuick.Window
import QtTest
import Quickshell
import Caelestia.Config
import qs.modules.bar.popouts
import qs.services
ShellRoot {
 Window {
  id: win; visible:true; width:470; height:media.implicitHeight+37; color:MenuStyle.taskbarSurface
  Rectangle { anchors.fill:parent; color: "#18212b" }
  Rectangle { anchors.fill:parent; color:MenuStyle.taskbarSurface; radius:28; border.width:1; border.color:MenuStyle.border }
  Component.onCompleted: { Colours.showPreview=true; Colours.previewLight=LIGHT; }
  Media { id:media; x:18.4; y:18.4; scaleOffset:1.15; fontScale:FONT; popouts:QtObject {} }
  TestCase {
   id: tests; name:"MediaControls"; when:false
   function test_controls() {
    if (EMPTY) { compare(media.player,null); verify(!findChild(media,"mediaSeek").enabled); console.log("MEDIA_CONTROLS_PASS"); return; }
    const player=media.player;
    const originalTitle=player.trackTitle;
    const originalArtist=player.trackArtist;
    const originalAlbum=player.trackAlbum;
    const companion=Players.alternative;
    player.trackTitle="You & Me • MEUTE";player.trackArtist="";player.trackAlbum="";
    companion.trackTitle="You & Me";companion.trackArtist="MEUTE";
    compare(media.artworkUrl,"file:///matching-cover.png");
    companion.trackTitle="Another song";compare(media.artworkUrl,"file:///browser-logo.png");
    companion.trackTitle="You & Me";companion.desktopEntry="another-app";
    compare(media.artworkUrl,"file:///browser-logo.png");
    companion.desktopEntry="chromium";
    companion.trackArtist="";compare(media.artworkUrl,"file:///browser-logo.png");
    player.trackTitle=originalTitle;player.trackArtist=originalArtist;player.trackAlbum=originalAlbum;
    console.log("MEDIA_ARTWORK_MATCH_PASS");
    const seek=findChild(media,"mediaSeek");
    mouseClick(seek,seek.width*0.75,seek.height/2); verify(player.position>180 && player.position<200);
    win.requestActivate(); wait(80); seek.forceActiveFocus(); keyClick(Qt.Key_Home); compare(player.position,0);
    keyClick(Qt.Key_End); compare(player.position,255);
    const play=findChild(media,"media-play_arrow");mouseClick(play);compare(player.isPlaying,true);
    player.isPlaying=false;
    mouseClick(findChild(media,"media-skip_next"));compare(player.nextCount,1);
    mouseClick(findChild(media,"media-skip_previous"));compare(player.previousCount,1);
    mouseClick(findChild(media,"media-shuffle"));compare(player.shuffle,true);
    mouseClick(findChild(media,"media-repeat"));compare(player.loopState,1);
    mouseClick(findChild(media,"media-repeat_one"));compare(player.loopState,2);
    mouseClick(findChild(media,"media-repeat"));compare(player.loopState,0);
    mouseWheel(media,media.width/2,media.height/2,0,120);verify(Audio.volume>0.5);
    const source=findChild(media,"mediaSource");mouseClick(source);
    const menu=findChild(win.contentItem,"mediaSourceMenu");
    verify(menu.expanded); menu.expanded=false;
    player.canSeek=false;verify(!seek.enabled);player.canSeek=true;
    player.shuffle=false;play.forceActiveFocus();
    player.position=102;wait(20);verify(Math.abs(seek.value-0.4)<0.01);
    console.log("MEDIA_CONTROLS_PASS");
   }
  }
  Timer { interval:300; running:true; onTriggered:tests.test_controls() }
  Timer { interval:900; running:true; onTriggered:{Colours.showPreview=true;Colours.previewLight=LIGHT;} }
  Timer { interval:1200; running:true; onTriggered: {
   console.log("MEDIA_LAYOUT",JSON.stringify({width:win.width,height:win.height,font:media.bodyPointSize,empty:EMPTY,light:Colours.light,surface:String(MenuStyle.taskbarSurface)}));
   win.contentItem.grabToImage(result=>{result.saveToFile(OUTPUT);Qt.quit();});
  } }
 }
}'''.replace('LIGHT',str(a.light).lower()).replace('FONT',str(a.font_scale)).replace('EMPTY',str(a.empty).lower()).replace('OUTPUT',json.dumps(str(a.out))))
 env=dict(os.environ,QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml'),QS_NO_RELOAD_POPUP='1',QS_DISABLE_CRASH_HANDLER='1')
 result=subprocess.run(['quickshell','-p',str(root)],env=env,text=True,capture_output=True,timeout=20)
 print(result.stdout+result.stderr)
 if not a.out.exists() or 'FAIL!' in result.stdout+result.stderr or ('MEDIA_CONTROLS_PASS' not in result.stdout+result.stderr):raise SystemExit(1)
