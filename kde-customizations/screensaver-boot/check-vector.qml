import QtQuick
import QtQuick.Window
import "wallpaper/contents/ui" as Ralleur
import "wallpaper/contents/ui/Engine.js" as Motion

Window {
    id: test
    width: 3840; height: 2160; visible: true
    property real stoppedAt: 0
    Ralleur.RalleurAnimation { id: animation; anchors.fill: parent }
    function check(engine) {
        for (const b of engine.bodies) {
            for (const value of [b.p.x,b.p.y,b.a,b.s.x,b.s.y]) {
                if (!Number.isFinite(value) || Math.abs(value) > 1000000) throw new Error("Unstable simulation")
            }
        }
    }
    Component.onCompleted: {
        try {
            const began = Date.now()
            const acts = ["arrival","burst","rain","shuffle","wave","migrate","snake"]
            for (const size of [[1920,1080],[3840,2160],[1440,2560],[5120,1440]]) {
                const engine = new Motion.Engine(size[0],size[1])
                for (const act of acts) {
                    // Settle into a known logo pose before each independent act.
                    for (const b of engine.bodies) { b.p=engine.home(b); b.v=Motion.v(0,0); b.a=0; b.av=0; b.s=Motion.v(1,1); b.sv=Motion.v(0,0); b.override=null; b.flag=false; b.bounce=false }
                    engine.start(act)
                    let frames=0
                    while (engine.act.name === act && frames < 3600) { engine.step(1/60); check(engine); frames++ }
                    if (frames === 3600) throw new Error("Act did not finish: "+act)
                }
                for (let i=0;i<18000;i++) { if(i===9000)engine.resize(size[1],size[0]); engine.step(i%2?1/30:1/120);check(engine) }
            }
            console.warn("PASS: all seven acts, four resolutions, resize and long random runs; "+(Date.now()-began)+" ms")
        } catch (error) { console.error(error); Qt.exit(1) }
    }
    Timer {
        interval: 1500; running: true
        onTriggered: {
            animation.animate=false
            for(let i=0;i<360;i++)animation.engine.step(1/60)
            animation.paintPose()
            test.stoppedAt=animation.engine.time
            verifyPause.start()
        }
    }
    Timer {
        id: verifyPause; interval: 150
        onTriggered: {
            if(animation.engine.time!==test.stoppedAt||animation.barCount!==8){console.error("Pause/render failed");Qt.exit(2);return}
            animation.grabToImage(function(result) {
                if(!result.saveToFile("/home/USER/ralleurOS/kde-customizations/screensaver-boot/backup/vector-4k.png")){Qt.exit(3);return}
                console.warn("PASS: 4K native vector render, eight bars, paused animation")
                Qt.quit()
            })
        }
    }
}
