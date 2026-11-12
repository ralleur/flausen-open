import { setupNavigation } from './navigation';
import { setupMotion } from './motion';
// Content, links and styling already exist before this enhancement loads.
setupNavigation();
setupMotion();
const wordmark = document.querySelector<HTMLImageElement>('.wordmark');
if (wordmark) {
  const fallback = () => wordmark.classList.add('failed');
  wordmark.addEventListener('error', fallback);
  if (wordmark.complete && !wordmark.naturalWidth) fallback();
}
