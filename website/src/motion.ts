type Spring = { element: SVGGElement; pivot: string; angle: number; velocity: number; limit: number };
export function setupMotion() {
 const preference = matchMedia('(prefers-reduced-motion: reduce)');
 const springs: Spring[] = [...document.querySelectorAll<SVGGElement>('[data-arm], [data-part]')].map(element => ({element,pivot:element.dataset.pivot!.split(' ').join(' '),angle:0,velocity:0,limit:element.hasAttribute('data-arm')?2:5}));
 let frame = 0, last = 0;
 let drag: {id:number; x:number; y:number; element:Element; spring:Spring; moved:boolean} | null = null;
 let suppressed: Element | null = null;
 const paint = (s:Spring) => s.element.setAttribute('transform', `rotate(${s.angle} ${s.pivot})`);
 const step = (now:number) => {
  const dt = Math.min((now-last)/1000 || 1/60, 1/30); last=now;
  let awake = false;
  for (const s of springs) {
   s.velocity += (-180*s.angle-23*s.velocity)*dt;
   s.angle = Math.max(-s.limit, Math.min(s.limit,s.angle+s.velocity*dt));
   if (Math.abs(s.angle)<.008 && Math.abs(s.velocity)<.04) {s.angle=0;s.velocity=0;} else awake=true;
   paint(s);
  }
  frame=awake?requestAnimationFrame(step):0;
 };
 const wake = () => {if (!frame && !preference.matches && !document.hidden) {last=performance.now();frame=requestAnimationFrame(step);}};
 const nudge = (element:Element, force=16) => {
  if (preference.matches || document.hidden) return;
  const part = element.closest<SVGGElement>('[data-part]');
  const arm = element.closest<SVGGElement>('[data-arm]');
  for (const s of springs) if (s.element===part || s.element===arm) s.velocity=Math.max(-35, Math.min(35,s.velocity+(s.element===arm?force*.23:force)));
  wake();
 };
 const release = () => {
  if (!drag) return;
  if (drag.element.hasPointerCapture(drag.id)) drag.element.releasePointerCapture(drag.id);
  drag=null;wake();
 };
 const reset = () => {
  release();cancelAnimationFrame(frame);frame=0;
  for (const s of springs) {s.angle=0;s.velocity=0;paint(s);}
 };
 document.querySelectorAll<SVGElement>('[data-interactive]').forEach(element => {
  element.addEventListener('pointerenter', event => {if(event.pointerType==='mouse') nudge(element,10);});
  element.addEventListener('pointerdown', event => {
   // Touch retains native vertical scrolling and immediate tap navigation.
   if (event.pointerType!=='mouse' || event.button!==0 || preference.matches) return;
   if (drag) {release();return;}
   const spring=springs.find(s=>s.element===element.closest('[data-part]'))!;
   drag={id:event.pointerId,x:event.clientX,y:event.clientY,element,spring,moved:false};
   suppressed=null;
  });
  element.addEventListener('pointermove', event => {
   if (!drag || event.pointerId!==drag.id) return;
   const distance=Math.hypot(event.clientX-drag.x,event.clientY-drag.y);
   if (!drag.moved && distance>6) {drag.moved=true;element.setPointerCapture(event.pointerId);}
   if (!drag.moved) return;
   drag.spring.angle=Math.max(-5,Math.min(5,(event.clientX-drag.x)*.045));
   drag.spring.velocity=0;paint(drag.spring);nudge(element,(event.clientX-drag.x)*.02);
   event.preventDefault();
  });
  element.addEventListener('click', event => {
   if (suppressed===element) {event.preventDefault();event.stopImmediatePropagation();suppressed=null;return;}
   if (element.getAttribute('role')==='button') nudge(element,32);
  });
  element.addEventListener('keydown', event => {
   if (element.getAttribute('role')==='button' && ['Enter',' '].includes(event.key)) {event.preventDefault();nudge(element,32);}
  });
 });
 document.addEventListener('pointerup', event => {
  if (drag?.id!==event.pointerId) return;
  if (drag.moved) suppressed=drag.element;
  release();
 });
 document.addEventListener('pointercancel', reset);
 window.addEventListener('blur', reset);
 document.addEventListener('visibilitychange', () => {if(document.hidden) reset();});
 preference.addEventListener('change', reset);
}
