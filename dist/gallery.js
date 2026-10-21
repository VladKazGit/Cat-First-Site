// Picture gallery (Knowledge comics): arrows and dots over a scroll-snap strip. Stores nothing, sends nothing.
document.querySelectorAll('[data-gallery]').forEach(function (g) {
  var track = g.querySelector('.gtrack'), count = track.children.length,
      dots = g.querySelectorAll('.gdots button'), prev = g.querySelector('.prev'), next = g.querySelector('.next');

  function current() { return Math.round(track.scrollLeft / track.clientWidth); }

  function go(i) {
    i = Math.max(0, Math.min(count - 1, i));
    track.scrollTo({left: i * track.clientWidth, behavior: 'smooth'});
  }

  function sync() {
    var i = current();
    dots.forEach(function (d, j) { d.setAttribute('aria-current', i === j ? 'true' : 'false'); });
    prev.disabled = i === 0;
    next.disabled = i === count - 1;
  }

  prev.addEventListener('click', function () { go(current() - 1); });
  next.addEventListener('click', function () { go(current() + 1); });
  dots.forEach(function (d, j) { d.addEventListener('click', function () { go(j); }); });
  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault();
      go(current() + (e.key === 'ArrowRight' ? 1 : -1));
    }
  });
  track.addEventListener('scroll', function () { window.requestAnimationFrame(sync); }, {passive: true});
  g.classList.add('js');
  sync();
});
