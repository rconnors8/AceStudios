/* ACE STUDIOS — site behaviour. No dependencies. */
(function () {
  'use strict';

  /* ---- mobile nav ---- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.getAttribute('data-open') === 'true';
      nav.setAttribute('data-open', String(!open));
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.textContent = open ? 'Menu' : 'Close';
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && nav.getAttribute('data-open') === 'true') {
        nav.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = 'Menu';
      }
    });
  }

  /* ---- scroll reveal ---- */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var targets = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var delay = Number(el.getAttribute('data-delay') || 0);
        setTimeout(function () { el.classList.add('is-in'); }, delay);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- work filters ---- */
  var filters = document.querySelectorAll('[data-filter]');
  var items = document.querySelectorAll('[data-tags]');
  if (filters.length && items.length) {
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-filter');
        filters.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        var shown = 0;
        items.forEach(function (item) {
          var tags = (item.getAttribute('data-tags') || '').split(/\s+/);
          var match = key === 'all' || tags.indexOf(key) !== -1;
          item.hidden = !match;
          if (match) shown++;
        });
        var count = document.querySelector('[data-count]');
        if (count) count.textContent = String(shown).padStart(2, '0');
      });
    });
  }

  /* ---- marquee: duplicate track so the loop is seamless ---- */
  document.querySelectorAll('.marquee__track').forEach(function (track) {
    track.innerHTML += track.innerHTML;
  });

  /* ---- local time in the colophon ---- */
  var clock = document.querySelector('[data-clock]');
  if (clock) {
    var tick = function () {
      clock.textContent = new Intl.DateTimeFormat('en-US', {
        hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/New_York'
      }).format(new Date()) + ' NYC';
    };
    tick();
    setInterval(tick, 30000);
  }

  /* ---- current year ---- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* ---- contact form (no backend: hand off to mail client) ---- */
  var form = document.querySelector('[data-contact-form]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var subject = 'New project enquiry — ' + (data.get('company') || data.get('name') || 'Untitled');
      var body = [
        'Name: ' + (data.get('name') || ''),
        'Company: ' + (data.get('company') || ''),
        'Email: ' + (data.get('email') || ''),
        'Scope: ' + (data.get('scope') || ''),
        'Budget: ' + (data.get('budget') || ''),
        '',
        data.get('message') || ''
      ].join('\n');
      window.location.href = 'mailto:studio@acestudios.design'
        + '?subject=' + encodeURIComponent(subject)
        + '&body=' + encodeURIComponent(body);
      var note = form.querySelector('[data-form-note]');
      if (note) note.textContent = 'Opening your mail client — if nothing happens, write to studio@acestudios.design directly.';
    });
  }
})();
