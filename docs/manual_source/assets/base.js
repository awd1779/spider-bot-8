
(function () {
  document.querySelectorAll('.copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var code = b.parentNode.querySelector('code').innerText;
      var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1500); };
      try {
        navigator.clipboard.writeText(code).then(done, function () { fallback(); });
      } catch (e) { fallback(); }
      function fallback() {
        var r = document.createRange(); r.selectNodeContents(b.parentNode.querySelector('code'));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        b.textContent = 'Press Ctrl+C';
      }
    });
  });
  var store = null;
  try { store = window.localStorage; store.getItem('x'); } catch (e) { store = null; }
  document.querySelectorAll('li.check input').forEach(function (cb) {
    var key = 'spider-manual-' + cb.dataset.k;
    try { if (store && store.getItem(key) === '1') cb.checked = true; } catch (e) {}
    cb.addEventListener('change', function () { try { if (store) store.setItem(key, cb.checked ? '1' : '0'); } catch (e) {} });
  });
  var links = Array.prototype.slice.call(document.querySelectorAll('nav a'));
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '0px 0px -70% 0px' });
    document.querySelectorAll('h2[id]').forEach(function (h) { obs.observe(h); });
  }
})();

