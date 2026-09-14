/* ACE STUDIOS — background field.
 *
 * A canvas of soft colour blobs and crisp dots sitting behind the whole site.
 * Depth-layered: everything moves against the scroll at its own rate, drifts
 * slowly on its own, and eases away from the cursor.
 *
 * Deliberately restrained — this sits behind the work, it does not compete
 * with it. Tune SETTINGS below.
 */
(function () {
  'use strict';

  var SETTINGS = {
    parallax: 0.42,    // how hard the field moves against the scroll (0 = static)
    drift: 0.10,       // idle movement when nothing is happening
    pointerRadius: 170, // cursor influence, px
    pointerPush: 26,   // how far the cursor shoves a dot, px
    dotAlpha: [0.12, 0.38],
    blobAlpha: 0.07,
    maxDots: 48
  };

  // pulled from the palette used by the cover plates
  var HUES = ['255, 75, 31', '43, 76, 255', '216, 255, 62', '224, 122, 60'];
  // large fields use the warmer/cooler hues only; lime is too loud at this size
  var BLOB_HUES = ['255, 75, 31', '43, 76, 255', '224, 122, 60'];
  var PAPER = '244, 242, 237';

  // Per-page opt-out: put data-bg="off" on <html> to keep a page completely
  // clean — useful if a piece of work needs the screen to itself.
  if (document.documentElement.getAttribute('data-bg') === 'off') return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canvas = document.createElement('canvas');
  canvas.className = 'bg-field';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.insertBefore(canvas, document.body.firstChild);

  var ctx = canvas.getContext('2d');
  var w = 0, h = 0, band = 0, dpr = 1;
  var dots = [], blobs = [];
  var pointer = { x: -9999, y: -9999, on: false };
  var last = 0, raf = null;

  function rand(a, b) { return a + Math.random() * (b - a); }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth;
    h = window.innerHeight;
    band = h * 1.7;               // virtual height the field wraps within
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
  }

  function build() {
    var count = Math.round(Math.min(SETTINGS.maxDots, Math.max(12, (w * h) / 26000)));
    if (w < 700) count = Math.round(count * 0.6);   // lighter on phones

    dots = [];
    for (var i = 0; i < count; i++) {
      var accent = Math.random() < 0.22;
      dots.push({
        x: rand(0, w),
        y: rand(0, band),
        r: accent ? rand(3, 7) : rand(1.5, 4.5),
        depth: rand(0.18, 0.85),
        alpha: rand(SETTINGS.dotAlpha[0], SETTINGS.dotAlpha[1]),
        ring: Math.random() < 0.3,
        hue: accent ? HUES[(Math.random() * HUES.length) | 0] : PAPER,
        vx: rand(-0.14, 0.14),
        vy: rand(-0.2, 0.2),
        ox: 0, oy: 0            // cursor displacement, springs back to zero
      });
    }

    blobs = [];
    var blobCount = w < 700 ? 2 : 4;
    for (var j = 0; j < blobCount; j++) {
      var hue = BLOB_HUES[j % BLOB_HUES.length];
      var radius = rand(0.18, 0.36) * Math.min(w, h);
      blobs.push({
        x: rand(0, w),
        y: rand(0, band),
        r: radius,
        depth: rand(0.08, 0.26),
        hue: hue,
        sprite: makeBlobSprite(hue, radius),
        vx: rand(-0.05, 0.05),
        vy: rand(-0.07, 0.07)
      });
    }
  }

  /* Blobs are drawn thousands of times but never change shape, so each one is
     rendered to its own small canvas once and then blitted. Rebuilding a radial
     gradient every frame was by far the most expensive thing in the loop. */
  function makeBlobSprite(hue, radius) {
    var size = Math.ceil(radius * 2);
    var off = document.createElement('canvas');
    off.width = off.height = Math.max(2, Math.ceil(size * dpr));
    var c = off.getContext('2d');
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    var g = c.createRadialGradient(radius, radius, 0, radius, radius, radius);
    g.addColorStop(0, 'rgba(' + hue + ',' + SETTINGS.blobAlpha + ')');
    g.addColorStop(0.55, 'rgba(' + hue + ',' + (SETTINGS.blobAlpha * 0.35) + ')');
    g.addColorStop(1, 'rgba(' + hue + ', 0)');
    c.fillStyle = g;
    c.beginPath();
    c.arc(radius, radius, radius, 0, Math.PI * 2);
    c.fill();
    return off;
  }

  function wrap(v, max) { return ((v % max) + max) % max; }

  function draw(dt) {
    var scroll = window.pageYOffset || document.documentElement.scrollTop || 0;
    ctx.clearRect(0, 0, w, h);

    var i, b, d, y, x;

    // soft colour fields first, furthest back
    for (i = 0; i < blobs.length; i++) {
      b = blobs[i];
      b.x += b.vx * dt * SETTINGS.drift;
      b.y += b.vy * dt * SETTINGS.drift;
      x = wrap(b.x, w + b.r * 2) - b.r;
      y = wrap(b.y - scroll * b.depth * SETTINGS.parallax, band + b.r * 2) - b.r;
      if (y + b.r < 0 || y - b.r > h) continue;
      ctx.drawImage(b.sprite, x - b.r, y - b.r, b.r * 2, b.r * 2);
    }

    // then the dots
    for (i = 0; i < dots.length; i++) {
      d = dots[i];
      d.x += d.vx * dt * SETTINGS.drift;
      d.y += d.vy * dt * SETTINGS.drift;

      x = wrap(d.x, w);
      y = wrap(d.y - scroll * d.depth * SETTINGS.parallax, band);
      if (y < -20 || y > h + 20) { d.ox *= 0.9; d.oy *= 0.9; continue; }

      if (pointer.on) {
        var dx = x - pointer.x, dy = y - pointer.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < SETTINGS.pointerRadius && dist > 0.01) {
          var force = (1 - dist / SETTINGS.pointerRadius) * SETTINGS.pointerPush;
          d.ox += ((dx / dist) * force - d.ox) * 0.12;
          d.oy += ((dy / dist) * force - d.oy) * 0.12;
        } else {
          d.ox *= 0.92; d.oy *= 0.92;
        }
      } else {
        d.ox *= 0.92; d.oy *= 0.92;
      }

      ctx.beginPath();
      ctx.arc(x + d.ox, y + d.oy, d.r, 0, Math.PI * 2);
      if (d.ring) {
        ctx.strokeStyle = 'rgba(' + d.hue + ',' + d.alpha + ')';
        ctx.lineWidth = 1;
        ctx.stroke();
      } else {
        ctx.fillStyle = 'rgba(' + d.hue + ',' + d.alpha + ')';
        ctx.fill();
      }
    }
  }

  function frame(now) {
    var dt = Math.min((now - last) || 16, 48) / 16;   // normalised to ~60fps
    last = now;
    draw(dt);
    raf = window.requestAnimationFrame(frame);
  }

  function start() {
    if (raf === null) { last = window.performance.now(); raf = window.requestAnimationFrame(frame); }
  }
  function stop() {
    if (raf !== null) { window.cancelAnimationFrame(raf); raf = null; }
  }

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      resize();
      if (reduce) draw(0);
    }, 180);
  });

  if (reduce) {
    // Motion is off: paint the field once so the page keeps its depth, then stop.
    resize();
    draw(0);
    return;
  }

  window.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;   // don't fight scrolling on phones
    pointer.x = e.clientX; pointer.y = e.clientY; pointer.on = true;
  }, { passive: true });
  window.addEventListener('pointerleave', function () { pointer.on = false; }, { passive: true });
  window.addEventListener('blur', function () { pointer.on = false; });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });

  resize();
  start();
})();
