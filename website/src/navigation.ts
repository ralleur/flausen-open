import content from './content.json';
export function setupNavigation() {
 const sections = [...document.querySelectorAll<HTMLElement>('.content section')];
 let invoker: HTMLElement | null = null;
 const route = (focus = false) => {
  const id = location.hash.slice(1);
  const reading = content.sections.some(section => section.id === id) || id === 'content';
  document.body.classList.toggle('reading', reading);
  document.querySelector<HTMLElement>('.stage')!.inert = reading;
  sections.forEach(section => section.hidden = reading && id !== 'content' && section.id !== id);
  if (reading) {
   const target = document.getElementById(id);
   if (focus) target?.focus({preventScroll:true});
   requestAnimationFrame(() => target?.scrollIntoView({block:'start'}));
  } else if (focus) {
   const visibleInvoker = invoker?.getClientRects().length ? invoker : [...document.querySelectorAll<HTMLElement>('.sculpture a[href="#play"]')].find(link => link.getClientRects().length > 0);
   visibleInvoker?.focus({preventScroll:true});
   window.scrollTo(0,0);
  }
 };
 document.addEventListener('click', event => {
  const link = (event.target as Element).closest('a[href^="#"]');
  if (link?.closest('.sculpture')) invoker = link as HTMLElement;
  if (link && link.getAttribute('href') === location.hash) route(true);
 });
 document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && document.body.classList.contains('reading')) {
   event.preventDefault(); location.hash = 'mobile';
  }
 });
 window.addEventListener('hashchange', () => route(true));
 document.body.classList.add('enhanced');
 route(!!location.hash);
}
