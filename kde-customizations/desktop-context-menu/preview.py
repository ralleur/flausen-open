#!/usr/bin/env python3
"""Render the installed menu in an isolated native window; never trigger actions."""
import json,os,subprocess,tempfile
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
args.out=args.out.resolve();args.out.parent.mkdir(parents=True,exist_ok=True)
shell=Path.home()/'.config/quickshell/caelestia'
with tempfile.TemporaryDirectory(prefix='desktop-context-preview-') as folder:
    root=Path(folder)
    for p in shell.iterdir():
        if p.name!='shell.qml':(root/p.name).symlink_to(p,target_is_directory=p.is_dir())
    (root/'shell.qml').write_text('''import QtQuick
import QtQuick.Window
import Quickshell
import qs.modules.background
import qs.services
ShellRoot {
    Window {
        visible:true;width:650;height:700;color:"#30383f"
        Item {id:anchor;x:40;y:40}
        DesktopContextMenu {id:menu;attachTo:anchor;expanded:true;revealHorizontal:false;maxHeight:600;screenName:"HDMI-A-2"}
        Timer {interval:1500;running:true;onTriggered:{
            const rows=[];
            function visit(item){
                if(item.text!==undefined && item.font!==undefined && item.visible)rows.push({text:item.text,font:item.font.family,pointSize:item.font.pointSize,italic:item.font.italic});
                for(const child of item.children ?? [])visit(child);
            }
            visit(menu.backgroundItem);
            menu.backgroundItem.grabToImage(result=>{
                const saved=result.saveToFile(Quickshell.env("MENU_PREVIEW_OUTPUT"));
                console.log("DESKTOP_MENU_PREVIEW",JSON.stringify({saved:saved,width:menu.backgroundItem.width,height:menu.backgroundItem.height,rows:rows,entries:menu.dynamicModel.map(item=>({text:item.text,visible:item.visible,footer:item.footerAction}))}));
                Qt.quit();
            });
        }}
        Timer {interval:10000;running:true;onTriggered:Qt.quit()}
    }
}
''')
    env=dict(os.environ,QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+folder,QS_NO_RELOAD_POPUP='1',QS_DISABLE_CRASH_HANDLER='1',MENU_PREVIEW_OUTPUT=str(args.out))
    result=subprocess.run(['quickshell','-p',folder],env=env,capture_output=True,text=True,timeout=15)
    lines=(result.stdout+result.stderr).splitlines();facts=next((json.loads(line.split('DESKTOP_MENU_PREVIEW ',1)[1]) for line in lines if 'DESKTOP_MENU_PREVIEW ' in line),None)
    errors=[line for line in lines if any(token in line for token in ['ReferenceError','TypeError','Error:', 'Binding loop'])]
    if not facts or not facts['saved'] or errors:raise RuntimeError('\n'.join(errors or lines[-20:]))
    assert facts['entries'][-1]['text']=='Menü anpassen' and facts['entries'][-1]['footer']
    footer=next(row for row in facts['rows'] if row['text']=='Menü anpassen')
    normal=next(row for row in facts['rows'] if row['text']!='Menü anpassen')
    assert footer['italic'] and footer['pointSize']<normal['pointSize']
    args.out.with_suffix('.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(facts,ensure_ascii=False))
