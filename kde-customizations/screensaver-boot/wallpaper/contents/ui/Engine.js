// Linux port of the supplied Swift engine's eight logo bars. No raster rendering.
var bars = [
    [0,0,58,22,"#2563C9"], [66,0,70,22,"#DF493F"],
    [4,34,22,62,"#DED6C8"], [38,34,22,62,"#E4AD22"],
    [72,34,22,62,"#278F8B"], [4,106,22,62,"#E56D2F"],
    [38,106,22,62,"#3F7D44"], [72,106,22,62,"#8F5B40"]
];
var pi = Math.PI;
function v(x,y) { return {x:x,y:y}; }
function add(a,b) { return v(a.x+b.x,a.y+b.y); }
function sub(a,b) { return v(a.x-b.x,a.y-b.y); }
function mul(a,k) { return v(a.x*k,a.y*k); }
function len(a) { return Math.sqrt(a.x*a.x+a.y*a.y); }
function norm(a) { var l=len(a); return l>1e-9?mul(a,1/l):v(1,0); }
function perp(a) { return v(-a.y,a.x); }
function mix(a,b,t) { return a+(b-a)*t; }
function vmix(a,b,t) { return add(a,mul(sub(b,a),t)); }
function clamp(t) { return Math.max(0,Math.min(1,t)); }
function smooth(t) { t=clamp(t);return t*t*(3-2*t); }
function ease(t) { t=clamp(t);return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2; }
function wrap(a,p) { return a-p*Math.round(a/p); }
function rand(a,b) { return a+Math.random()*(b-a); }
function ri(n) { return Math.floor(Math.random()*n); }
function shuffle(a) { a=a.slice();for(var i=a.length-1;i>0;i--){var j=ri(i+1),q=a[i];a[i]=a[j];a[j]=q;}return a; }
function spring(b,k,z,ak,az) { b.mode="spring";b.k=k;b.z=z;b.ak=ak===undefined?k:ak;b.az=az===undefined?z:az; }
function script(b,p,a,s,dt) {
    if(b.mode==="scripted"&&dt>0){b.v=mul(sub(p,b.p),1/dt);b.av=(a-b.a)/dt;}
    b.mode="scripted";b.p=p;b.a=a;b.override=s;
}
function hop(a,b,u,height,lift,halfH) {
    var sy=1,p,w;
    if(u<0.16){sy=1-0.26*Math.sin(pi*u/0.16*0.5);p=a;}
    else if(u<0.84){w=(u-0.16)/0.68;p=add(vmix(a,b,ease(w)),mul(lift,height*Math.sin(pi*w)));sy=1+0.2*Math.sin(pi*w)*(1-0.6*w);}
    else{w=(u-0.84)/0.16;sy=1-0.24*Math.sin(pi*w);p=b;}
    p=v(p.x,p.y+(lift.y<0?halfH*(1-sy):0));
    return {p:p,s:v(1+(1-sy)*0.7,sy)};
}
function Engine(width,height) {
    this.bodies=bars.map(function(g,i){return {i:i,w:g[2],h:g[3],home:v(g[0]+g[2]/2-68,g[1]+g[3]/2-84),
        radius:Math.hypot(g[2],g[3])/2,p:v(0,0),v:v(0,0),a:0,av:0,s:v(1,1),sv:v(0,0),override:null,
        mode:"spring",target:v(0,0),ta:0,k:140,z:0.6,ak:140,az:0.6,gravity:0,drag:0,angDrag:0,bounce:false,flag:false,
        phase:i*0.7+(g[0]+g[2]/2-68)*0.02};});
    this.time=0;this.origin=v(0,0);this.history=[];this.sinceMove=0;
    this.resize(width,height);this.origin=this.startOrigin();this.start("arrival");
}
Engine.prototype.startOrigin=function(){
    // Assemble in a random corner, clear of the central authentication card.
    // Include the entire logo's half-size plus margin, with a little variation.
    var x=88+rand(0,this.world.x*0.045),y=104+rand(0,this.world.y*0.045);
    return v(Math.random()<0.5?x:this.world.x-x,Math.random()<0.5?y:this.world.y-y);
};
Engine.prototype.resize=function(width,height){
    this.unit=Math.min(Math.max(height,1)*0.3/168,Math.max(width,1)*0.42/136);
    this.world=v(Math.max(width,1)/this.unit,Math.max(height,1)/this.unit);
    if(this.origin.x<88||this.origin.x>this.world.x-88||this.origin.y<104||this.origin.y>this.world.y-104)this.origin=this.startOrigin();
};
Engine.prototype.home=function(b,o){return add(o||this.origin,b.home);};
Engine.prototype.idle=function(b,o){return add(this.home(b,o),v(0,1.1*Math.sin(1.7*this.time+b.phase)));};
Engine.prototype.destination=function(distance){
    var best=this.origin,bestD=-1;
    for(var i=0;i<40;i++){var c=v(rand(98,this.world.x-98),rand(114,this.world.y-114)),d=len(sub(c,this.origin));if(d>=distance)return c;if(d>bestD){best=c;bestD=d;}}
    return best;
};
Engine.prototype.choose=function(){
    var movers=["rain","migrate","snake"],pool=this.sinceMove>=2?movers:movers.concat(["burst","shuffle","wave"]);
    var recent=this.history.slice(-3),options=pool.filter(function(n){return recent.indexOf(n)<0;});
    if(!options.length)options=pool;return options[ri(options.length)];
};
Engine.prototype.next=function(){
    var n=this.act.name;
    if(["rain","migrate","snake"].indexOf(n)>=0)this.sinceMove=0;else if(n!=="hold")this.sinceMove++;
    if(n!=="hold")this.start("hold");else{n=this.choose();this.history.push(n);this.history=this.history.slice(-3);this.start(n);}
};
Engine.prototype.start=function(name){
    var a=this.act={name:name,t:0,done:false},e=this,bs=this.bodies;
    if(name==="hold"){
        a.duration=this.history.length?rand(5,7.5):5;a.fidget=rand(1,2.2);
        bs.forEach(function(b){spring(b,140,0.6);b.override=null;b.a=wrap(b.a,pi);b.ta=0;});
    }else if(name==="arrival"){
        a.launch=[];shuffle([0,1,2,3,4,5,6,7]).forEach(function(i,n){var b=bs[i],ang=rand(0,2*pi);b.p=add(e.origin,mul(v(Math.cos(ang),Math.sin(ang)),len(e.world)*0.5+140));b.a=rand(-3,3)*pi;b.mode="parked";a.launch[i]=0.35+n*0.14;});
    }else if(name==="burst"){
        a.released=false;a.returnAt=[];bs.forEach(function(b){spring(b,260,0.7);b.flag=false;});shuffle([0,1,2,3,4,5,6,7]).forEach(function(i,n){a.returnAt[i]=3+n*0.06;});
    }else if(name==="rain"){
        a.phase=0;a.dropAt=[];a.to=this.destination(this.world.x*0.22);bs.forEach(function(b){b.flag=false;b.t0=rand(0,0.45);});
    }else if(name==="shuffle"){
        a.perm=[2,3,4,5,6,7];a.slots=a.perm.map(function(i){return bs[i].home;});a.swaps=[];a.current=0;a.swapStart=0.5;
        var p=a.perm.slice(),last="";
        for(var j=0;j<6;j++){var x,y,key;do{x=ri(6);y=ri(6);key=Math.min(x,y)+","+Math.max(x,y);}while(x===y||key===last);last=key;var tmp=p[x];p[x]=p[y];p[y]=tmp;a.swaps.push([x,y,Math.random()<0.4]);}
        for(var s=0;s<6;s++)if(p[s]!==s+2){var from=p.indexOf(s+2),q=p[s];p[s]=p[from];p[from]=q;a.swaps.push([s,from,Math.random()<0.25]);}
        bs.forEach(function(b){spring(b,160,0.6);});
    }else if(name==="wave"){
        a.minX=Math.min.apply(null,bs.map(function(b){return b.home.x;}));a.width=Math.max.apply(null,bs.map(function(b){return b.home.x;}))-a.minX;
        bs.forEach(function(b){spring(b,200,0.55);});
    }else if(name==="migrate"){
        a.from=this.origin;a.to=this.destination(this.world.x*0.3);a.starts=[];a.counts=[];a.durations=[];a.finish=0;
        var distance=len(sub(a.to,a.from));bs.forEach(function(b){spring(b,160,0.6);a.starts[b.i]=rand(0.2,0.7);a.counts[b.i]=Math.max(2,Math.round(distance/64));a.durations[b.i]=0.34;a.finish=Math.max(a.finish,a.starts[b.i]+a.counts[b.i]*0.34+1.4);});
    }else if(name==="snake"){
        this.startSnake(a);
    }
};
Engine.prototype.update=function(dt){
    var e=this,a=this.act,t=a.t,bs=this.bodies;
    if(a.name==="hold"){
        bs.forEach(function(b){b.target=e.idle(b);});
        if(t>=a.fidget){var b=bs[ri(8)];switch(ri(4)){case 0:b.v.y-=150;b.sv=add(b.sv,v(-2.5,3.5));break;case 1:b.av+=(Math.random()<0.5?1:-1)*rand(4,7);break;case 2:b.sv=add(b.sv,v(4.5,-5.5));break;default:b.av+=(Math.random()<0.5?1:-1)*2*pi*3.2;b.v.y-=120;}a.fidget=t+rand(1.4,3);}
        a.done=t>=a.duration;
    }else if(a.name==="arrival"){
        bs.forEach(function(b){b.target=e.idle(b);b.ta=0;if(b.mode==="parked"&&t>=a.launch[b.i]){spring(b,36,0.42,28,0.4);b.v=mul(perp(norm(sub(b.target,b.p))),rand(250,520)*(Math.random()<0.5?1:-1));}if(b.mode!=="parked"&&!b.flag&&len(sub(b.p,b.target))<4){b.flag=true;b.sv=add(b.sv,mul(v(5,-7),Math.min(1,len(b.v)/260)));}});a.done=t>4.6;
    }else if(a.name==="burst"){
        if(t<0.55){var squeeze=smooth(t/0.55);bs.forEach(function(b){b.target=add(e.origin,mul(b.home,1-0.14*squeeze));b.ta=0;b.override=v(1+0.05*squeeze,1-0.12*squeeze);});}
        else if(!a.released){a.released=true;bs.forEach(function(b){b.override=null;b.sv=v(-3,5);b.mode="ballistic";b.gravity=0;b.drag=1.1;b.angDrag=0.6;b.bounce=true;b.v=add(mul(norm(sub(b.p,e.origin)),rand(520,900)),v(rand(-90,90),rand(-90,90)));b.av=rand(-9,9);});}
        else bs.forEach(function(b){if(t>=a.returnAt[b.i]){if(!b.flag){b.flag=true;b.a=wrap(b.a,pi);b.bounce=false;spring(b,55,0.4,45,0.45);}b.target=e.idle(b);b.ta=0;}});a.done=t>6.2;
    }else if(a.name==="rain"){
        if(a.phase===0){bs.forEach(function(b){if(b.mode!=="ballistic"){b.target=e.idle(b);if(t>=b.t0){b.mode="ballistic";b.gravity=2200;b.drag=0;b.angDrag=0;b.bounce=false;b.v=v(rand(-110,110),rand(-420,-160));b.av=rand(-6,6);b.sv=add(b.sv,v(-2,4));}}});
            if(t>4||bs.every(function(b){return b.mode==="ballistic"&&b.p.y>e.world.y+b.radius+10;})){
                a.phase=1;a.phaseStart=t;e.origin=a.to;var at=0.25;
                [[5,6,7],[2,3,4],[0,1]].forEach(function(row){shuffle(row).forEach(function(i,n){a.dropAt[i]=at+n*0.11;});at+=0.62;});
                bs.forEach(function(b){b.mode="parked";b.a=0;b.av=0;b.v=v(0,0);b.p=v(e.home(b).x,-b.radius-20);b.flag=false;});
            }
        }else{
            var lt=t-a.phaseStart;
            bs.forEach(function(b){var home=e.home(b);if(b.mode==="parked"&&lt>=a.dropAt[b.i]){b.mode="ballistic";b.gravity=3200;b.drag=0;b.angDrag=0;b.v=v(0,250);b.override=v(0.86,1.18);}if(b.mode==="ballistic"&&!b.flag&&b.p.y>=home.y){b.flag=true;var impact=Math.min(1.3,b.v.y/1400);b.p.y=home.y;b.v=v(0,0);b.override=null;b.s=v(1+0.3*impact,1-0.38*impact);b.sv=v(0,0);spring(b,260,0.5);bs.forEach(function(o){if(o.flag&&o!==b&&o.home.y>b.home.y){o.sv=add(o.sv,mul(v(2.2,-3.2),impact));o.v.y+=40*impact;}});}if(b.flag){b.target=e.idle(b);b.ta=0;}});
            a.done=lt>Math.max.apply(null,a.dropAt)+1.6;
        }
    }else if(a.name==="shuffle"){
        var sorting=a.current>=6,dur=sorting?0.5:0.62,active=[],focus=null;
        if(a.current<a.swaps.length&&t>=a.swapStart){var swap=a.swaps[a.current],sa=swap[0],sb=swap[1],A=bs[a.perm[sa]],B=bs[a.perm[sb]],pa=add(e.origin,a.slots[sa]),pb=add(e.origin,a.slots[sb]),u=(t-a.swapStart)/dur;
            if(u<1){var lift=perp(norm(sub(pb,pa)));if(lift.y>0)lift=mul(lift,-1);var d=len(sub(pb,pa)),ra=hop(pa,pb,u,26+d*0.28,lift,A.h/2),rb=hop(pb,pa,u,10+d*0.12,mul(lift,-1),B.h/2);script(A,ra.p,swap[2]?-2*pi*ease(clamp((u-0.16)/0.68)):0,ra.s,dt);script(B,rb.p,0,rb.s,dt);active=[A.i,B.i];focus=vmix(pa,pb,0.5);}
            else{var old=a.perm[sa];a.perm[sa]=a.perm[sb];a.perm[sb]=old;[A,B].forEach(function(b){b.a=0;b.v=v(0,0);b.av=0;b.override=null;b.sv=v(3,-4);spring(b,200,0.5);});a.current++;a.swapStart=t+(a.current===6?0.7:sorting?0.08:0.12);}
        }
        bs.forEach(function(b){if(active.indexOf(b.i)<0){var slot=a.perm.indexOf(b.i);b.target=slot>=0?add(add(e.origin,a.slots[slot]),v(0,1.1*Math.sin(1.7*e.time+b.phase))):e.idle(b);b.ta=0;}});
        if(focus)[0,1].forEach(function(i){bs[i].ta=Math.max(-0.16,Math.min(0.16,(focus.x-e.home(bs[i]).x)*0.004));bs[i].target=add(e.idle(bs[i]),v(0,-2));});
        a.done=a.current>=a.swaps.length&&t>a.swapStart+0.8;
    }else if(a.name==="wave"){
        bs.forEach(function(b){var nx=(b.home.x-a.minX)/a.width,home=e.home(b),u1=(t-(0.2+nx*0.85))/0.52,u2=(t-(2+(1-nx)*0.85))/0.62,r;
            if(u1>0&&u1<1){r=hop(home,home,u1,30,v(0,-1),b.h/2);script(b,r.p,0,r.s,dt);}else if(u2>0&&u2<1){r=hop(home,home,u2,22,v(0,-1),b.h/2);script(b,r.p,2*pi*ease(clamp((u2-0.16)/0.68)),r.s,dt);}else{if(b.mode==="scripted"){b.a=0;b.av=0;b.v=v(0,0);b.override=null;spring(b,200,0.55);}b.target=e.idle(b);b.ta=0;}});a.done=t>4.3;
    }else if(a.name==="migrate"){
        bs.forEach(function(b){var i=b.i,from=add(a.from,b.home),to=add(a.to,b.home),lt=t-a.starts[i],total=a.counts[i]*a.durations[i];
            if(lt<=0){b.target=e.idle(b,a.from);b.ta=0;}else if(lt<total){var k=Math.floor(lt/a.durations[i]),u=(lt-k*a.durations[i])/a.durations[i],n=a.counts[i],r=hop(vmix(from,to,k/n),vmix(from,to,(k+1)/n),u,28,v(0,-1),b.h/2);script(b,r.p,(to.x>from.x?1:-1)*0.18*Math.sin(pi*clamp((u-0.16)/0.68)),r.s,dt);}else{if(b.mode==="scripted"){b.v=v(0,0);b.av=0;b.a=0;b.override=null;spring(b,200,0.55);}b.target=e.idle(b,a.to);b.ta=0;}});if(t>a.finish){e.origin=a.to;a.done=true;}
    }else if(a.name==="snake")this.updateSnake(a,dt);
};
Engine.prototype.startSnake=function(a){
    var e=this,bs=this.bodies;a.from=this.origin;a.to=this.destination(this.world.x*0.25);
    var c=mul(this.world,0.5),rx=this.world.x/2-90,ry=this.world.y/2-80,start=this.home(bs[0]),wps=[start],dir=Math.random()<0.5?1:-1,theta=Math.atan2((start.y-c.y)/ry,(start.x-c.x)/rx);
    for(var i=0;i<6;i++){theta+=dir*rand(1.15,1.6);var r=rand(0.55,1)*(i%2===0?1:0.75);wps.push(add(c,v(Math.cos(theta)*rx*r,Math.sin(theta)*ry*r)));}wps.push(a.to);
    var ctrl=[sub(mul(wps[0],2),wps[1])].concat(wps).concat([sub(mul(wps[wps.length-1],2),wps[wps.length-2])]);a.pts=[];
    for(i=1;i<ctrl.length-2;i++){
        var p0=ctrl[i-1],p1=ctrl[i],p2=ctrl[i+1],p3=ctrl[i+2],t0=0,t1=Math.max(1e-3,Math.sqrt(len(sub(p1,p0)))),t2=t1+Math.max(1e-3,Math.sqrt(len(sub(p2,p1)))),t3=t2+Math.max(1e-3,Math.sqrt(len(sub(p3,p2))));
        for(var s=0;s<120;s++){var t=mix(t1,t2,s/120),a1=vmix(p0,p1,(t-t0)/(t1-t0)),a2=vmix(p1,p2,(t-t1)/(t2-t1)),a3=vmix(p2,p3,(t-t2)/(t3-t2)),b1=vmix(a1,a2,(t-t0)/(t2-t0)),b2=vmix(a2,a3,(t-t1)/(t3-t1));a.pts.push(vmix(b1,b2,(t-t1)/(t2-t1)));}
    }
    a.pts.push(wps[wps.length-1]);a.cum=[0];a.angles=[];var prev=0;
    for(i=0;i<a.pts.length;i++){if(i>0)a.cum.push(a.cum[i-1]+len(sub(a.pts[i],a.pts[i-1])));var d=sub(a.pts[Math.min(i+1,a.pts.length-1)],a.pts[Math.max(i-1,0)]),angle=Math.atan2(d.y,d.x);if(i>0)angle=prev+wrap(angle-prev,2*pi);a.angles.push(angle);prev=angle;}
    a.length=a.cum[a.cum.length-1];a.speed=Math.max(380,Math.min(620,a.length/7));a.offset=[0];a.angOff=[];a.joined=[];a.joinT=[];a.released=[];a.allReleased=null;
    bs.forEach(function(b,i){if(i>0)a.offset[i]=a.offset[i-1]+Math.max(bs[i-1].w,bs[i-1].h)/2+8+Math.max(b.w,b.h)/2;a.angOff[i]=0;a.joined[i]=false;a.joinT[i]=0;a.released[i]=false;spring(b,160,0.6);});
};
Engine.prototype.pathAt=function(a,s){
    s=Math.max(0,Math.min(a.length,s));var lo=0,hi=a.cum.length-1;while(hi-lo>1){var mid=Math.floor((lo+hi)/2);if(a.cum[mid]<=s)lo=mid;else hi=mid;}
    var f=(s-a.cum[lo])/Math.max(a.cum[hi]-a.cum[lo],1e-9);return {p:vmix(a.pts[lo],a.pts[hi],f),a:mix(a.angles[lo],a.angles[hi],f)};
};
Engine.prototype.updateSnake=function(a,dt){
    var e=this,t=a.t,tt=Math.max(0,t-0.4),lead=tt<0.9?a.speed*tt*tt/1.8:a.speed*(tt-0.45);
    this.bodies.forEach(function(b){var i=b.i;if(a.released[i]){b.target=e.idle(b,a.to);b.ta=0;return;}var s=lead-a.offset[i];if(s>=a.length){a.released[i]=true;b.a=wrap(b.a,pi);spring(b,70,0.42,60,0.5);b.target=e.idle(b,a.to);b.ta=0;b.sv=add(b.sv,v(3,-4));}else if(s>0){var q=e.pathAt(a,s);if(!a.joined[i]){a.joined[i]=true;a.joinT[i]=t;var base=b.w>=b.h?0:pi/2;a.angOff[i]=base+pi*Math.round((b.a-(q.a+base))/pi);b.sv=add(b.sv,v(-3,4));}var j=smooth((t-a.joinT[i])/0.6);spring(b,mix(40,900,j),mix(0.55,0.85,j),mix(40,700,j),0.8);b.target=q.p;b.ta=q.a+a.angOff[i];}else{b.target=e.idle(b,a.from);b.ta=0;}});
    if(a.allReleased===null&&a.released.every(function(r){return r;})){a.allReleased=t;e.origin=a.to;}if(a.allReleased!==null&&t>a.allReleased+2.2)a.done=true;
};
Engine.prototype.step=function(rawDt){
    var dt=Math.min(Math.max(rawDt,0),1/15);if(!dt)return;this.time+=dt;this.act.t+=dt;this.update(dt);if(this.act.done)this.next();
    var n=Math.max(1,Math.ceil(dt*240)),h=dt/n,bs=this.bodies;
    for(var j=0;j<n;j++)for(var i=0;i<8;i++){
        var b=bs[i];if(b.mode==="spring"){
            var c=2*b.z*Math.sqrt(b.k),ac=2*b.az*Math.sqrt(b.ak);
            b.v.x+=(-b.k*(b.p.x-b.target.x)-c*b.v.x)*h;b.v.y+=(-b.k*(b.p.y-b.target.y)-c*b.v.y)*h;
            b.p.x+=b.v.x*h;b.p.y+=b.v.y*h;b.av+=(-b.ak*(b.a-b.ta)-ac*b.av)*h;b.a+=b.av*h;
        }else if(b.mode==="ballistic"){
            b.v.y+=b.gravity*h;var drag=Math.exp(-b.drag*h);b.v.x*=drag;b.v.y*=drag;b.p.x+=b.v.x*h;b.p.y+=b.v.y*h;b.av*=Math.exp(-b.angDrag*h);b.a+=b.av*h;
            if(b.bounce){var r=b.radius*0.8;if(b.p.x<r){b.p.x=r;b.v.x=Math.abs(b.v.x)*0.85;b.av*=-0.7;}if(b.p.x>this.world.x-r){b.p.x=this.world.x-r;b.v.x=-Math.abs(b.v.x)*0.85;b.av*=-0.7;}if(b.p.y<r){b.p.y=r;b.v.y=Math.abs(b.v.y)*0.85;b.av*=-0.7;}if(b.p.y>this.world.y-r){b.p.y=this.world.y-r;b.v.y=-Math.abs(b.v.y)*0.85;b.av*=-0.7;}}
        }
        if(b.override){b.s.x=b.override.x;b.s.y=b.override.y;b.sv.x=0;b.sv.y=0;}else{var damping=2*0.28*Math.sqrt(420);b.sv.x+=(-420*(b.s.x-1)-damping*b.sv.x)*h;b.sv.y+=(-420*(b.s.y-1)-damping*b.sv.y)*h;b.s.x+=b.sv.x*h;b.s.y+=b.sv.y*h;}
    }
};
