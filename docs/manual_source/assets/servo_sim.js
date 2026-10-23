(function () {
  var root = document.getElementById('servoSim'); if (!root) return;
  var slider = document.getElementById('angle'), angOut = document.getElementById('angOut');
  var usOut = document.getElementById('usOut'), moveOut = document.getElementById('moveOut');
  var dot = document.getElementById('dot'), guide = document.getElementById('guide');
  var wave = document.getElementById('wave'), wArrow = document.getElementById('wArrow'), wLabel = document.getElementById('wLabel');
  var horn = document.getElementById('horn');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var volts = '4.8', degPerSec = 600, shown = 90, target = 90, last = null, moving = false;
  function us(a) { return Math.round(500 + a * 1900 / 180); }
  function draw(a) {
    var x = 50 + a / 180 * 235, p = us(a), y = 180 - (p - 500) / 1900 * 150;
    dot.setAttribute('cx', x); dot.setAttribute('cy', y);
    guide.setAttribute('d', 'M' + x + ' 180V' + y + 'H50');
    var wx = 40 + p / 3000 * 250;
    wave.setAttribute('d', 'M40 170V60H' + wx + 'V170H290');
    wArrow.setAttribute('d', 'M40 40H' + wx);
    wLabel.setAttribute('x', (40 + wx) / 2); wLabel.textContent = p + ' µs';
  }
  function drawHorn(a) { horn.setAttribute('transform', 'rotate(' + (a - 90) + ' 150 160)'); }
  function setTarget(a) {
    var move = Math.abs(a - shown);
    target = a; angOut.textContent = a + '°'; usOut.textContent = us(a) + ' µs'; slider.value = a; draw(a);
    moveOut.textContent = 'At ' + volts + ' V: ' + move.toFixed(0) + '° takes about ' + (move / degPerSec).toFixed(2) + ' s';
    if (reduce) { shown = target; drawHorn(shown); return; }
    if (!moving) { moving = true; last = null; requestAnimationFrame(tick); }
  }
  function tick(t) {
    if (last === null) last = t;
    var dt = (t - last) / 1000; last = t;
    var step = degPerSec * dt, d = target - shown;
    if (Math.abs(d) <= step) { shown = target; moving = false; } else { shown += d > 0 ? step : -step; }
    drawHorn(shown);
    if (moving) requestAnimationFrame(tick);
  }
  slider.addEventListener('input', function () { setTarget(parseInt(slider.value, 10)); });
  root.querySelectorAll('[data-a]').forEach(function (b) { b.addEventListener('click', function () { setTarget(parseInt(b.dataset.a, 10)); }); });
  root.querySelectorAll('[data-v]').forEach(function (b) {
    b.addEventListener('click', function () {
      root.querySelectorAll('[data-v]').forEach(function (x) { x.classList.toggle('on', x === b); });
      volts = b.dataset.v === '6' ? '6.0' : '4.8';
      degPerSec = b.dataset.v === '6' ? 750 : 600;
      moveOut.textContent = volts + ' V: 60° in ' + (b.dataset.v === '6' ? '0.08' : '0.10') + ' s. Same angle, different speed.';
    });
  });
  draw(90); drawHorn(90);
})();

