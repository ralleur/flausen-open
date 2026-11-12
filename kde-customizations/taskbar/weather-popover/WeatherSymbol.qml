import QtQuick
import qs.services

// Small vector weather drawings; independent of the icon font and theme assets.
Canvas {
    id: root
    property string condition: "cloud"
    property color ink: MenuStyle.ink
    property color sun: "#f2be66"
    property color water: "#91c8e8"
    onConditionChanged: requestPaint()
    onInkChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        const c=getContext("2d");c.reset();c.scale(width/100,height/100);
        c.lineWidth=4;c.lineCap="round";c.lineJoin="round";
        if(condition==="location") {
            c.strokeStyle=root.ink;c.lineWidth=6;c.beginPath();c.moveTo(50,91);
            c.bezierCurveTo(44,81,20,56,20,36);c.bezierCurveTo(20,0,80,0,80,36);
            c.bezierCurveTo(80,56,56,81,50,91);c.stroke();
            c.beginPath();c.arc(50,35,10,0,Math.PI*2);c.stroke();return;
        }
        const night=condition.indexOf("night")>=0;
        const clear=condition.indexOf("clear")>=0;
        const partly=condition.indexOf("partly")>=0;
        function line(x,y,x2,y2) { c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke(); }
        if (clear || partly) {
            const x=partly?65:50,y=partly?34:48,r=partly?18:24;
            c.strokeStyle=night?root.ink:root.sun;
            if (night) {
                c.beginPath();c.moveTo(x+8,y-r);c.bezierCurveTo(x-24,y-r-2,x-29,y+25,x+6,y+24);
                c.bezierCurveTo(x+21,y+23,x+27,y+12,x+26,y+6);c.bezierCurveTo(x+2,y+17,x-5,y-5,x+8,y-r);c.stroke();
            } else {
                c.beginPath();c.arc(x,y,r,partly?-Math.PI:0,partly?Math.PI*.2:Math.PI*2);c.stroke();
                for(let i=0;i<8;i++) {const a=i*Math.PI/4;if(partly && a>Math.PI*.2 && a<Math.PI)continue;line(x+Math.cos(a)*(r+8),y+Math.sin(a)*(r+8),x+Math.cos(a)*(r+16),y+Math.sin(a)*(r+16));}
            }
        }
        if (!clear || partly) {
            const rain=/rain|snow|thunder/.test(condition);
            const y=rain?47:62;
            if (condition==="air") {
                c.strokeStyle=root.water;
                line(12,36,64,36);line(20,50,85,50);line(12,64,67,64);
                return;
            }
            c.strokeStyle=root.ink;
            c.beginPath();c.moveTo(24,y+17);c.bezierCurveTo(3,y+17,4,y-9,23,y-9);
            c.bezierCurveTo(26,y-35,60,y-37,68,y-12);c.bezierCurveTo(93,y-14,97,y+17,74,y+17);c.closePath();c.stroke();
            if (/rain/.test(condition)) { c.strokeStyle=root.water;for(let i=0;i<3;i++)line(30+i*20,74,25+i*20,85); }
            if (/snow/.test(condition)) {c.strokeStyle=root.water;for(let i=0;i<3;i++){line(29+i*21,77,29+i*21,88);line(24+i*21,82,34+i*21,82);}}
            if (/thunder/.test(condition)) {c.strokeStyle=root.sun;c.beginPath();c.moveTo(52,68);c.lineTo(39,83);c.lineTo(54,83);c.lineTo(44,96);c.stroke();}
            if (condition==="foggy") {c.strokeStyle=root.ink;line(18,85,82,85);line(27,94,73,94);}
        }
    }
}
