const stage = document.querySelector('.scenery');
const video = stage.querySelector('video');
const journey = document.querySelector('#journey');
const chapters = [...journey.querySelectorAll('section')];
const links = [...document.querySelectorAll('nav a')];
const picker = document.querySelector('input[type=file]');
const status = document.querySelector('.status');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const frameTolerance = 1 / 30;

let scheduled = false;
let localVideo;
let activeChapter = 0;

function paint() {
  scheduled = false;
  const scrollRange = Math.max(1, journey.offsetHeight - window.innerHeight);
  const progress = Math.max(0, Math.min(1, window.scrollY / scrollRange));
  const midpoint = window.innerHeight / 2;
  activeChapter = Math.max(0, chapters.findLastIndex(chapter => chapter.getBoundingClientRect().top <= midpoint));

  document.documentElement.style.setProperty('--progress', progress);
  stage.style.setProperty('--zoom', reducedMotion.matches ? 1 : 1 + Math.min(progress, .5) * .22);
  stage.style.setProperty('--inside', reducedMotion.matches ? Number(activeChapter === 2) : Math.max(0, (progress - .5) * 2));
  links.forEach((link, index) => {
    if (index === activeChapter) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });

  const canSeek = !reducedMotion.matches && !video.error && Number.isFinite(video.duration) && video.duration > 0;
  stage.classList.toggle('has-video', canSeek && video.readyState >= 2);
  if (!canSeek || video.seeking) return;

  const target = progress * Math.max(0, video.duration - frameTolerance);
  if (Math.abs(video.currentTime - target) >= frameTolerance / 2) video.currentTime = target;
}

function schedulePaint() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(paint);
}

window.addEventListener('scroll', schedulePaint, { passive: true });
window.addEventListener('resize', schedulePaint);
reducedMotion.addEventListener('change', schedulePaint);
for (const event of ['loadedmetadata', 'loadeddata', 'seeked', 'canplay', 'emptied', 'error']) {
  video.addEventListener(event, schedulePaint);
}

video.addEventListener('loadeddata', () => {
  if (localVideo) status.textContent = reducedMotion.matches ? 'Reduced motion is on' : 'Local MP4 loaded';
});
video.addEventListener('error', () => {
  if (localVideo) status.textContent = 'This MP4 could not be played';
});

picker.addEventListener('change', () => {
  const file = picker.files[0];
  if (!file) return;
  if (localVideo) URL.revokeObjectURL(localVideo);
  localVideo = URL.createObjectURL(file);
  status.textContent = 'Loading local MP4…';
  video.src = localVideo;
  video.load();
});

if (document.body.dataset.film) video.src = document.body.dataset.film;
schedulePaint();
