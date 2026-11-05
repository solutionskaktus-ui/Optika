/* ============================================
   OPTIKA VISAGE, main.js
   Meni, tablica za vid (dioptrija), reveal, godina
   ============================================ */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- GA4: klikovi na kontakt ----------
  function track(method) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'contact_click', { method: method });
    }
  }
  document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
    a.addEventListener('click', function () { track('phone'); });
  });
  document.querySelectorAll('a[href^="viber://"]').forEach(function (a) {
    a.addEventListener('click', function () { track('viber'); });
  });
  document.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
    a.addEventListener('click', function () { track('email'); });
  });

  // ---------- Nav: senka pri skrolu ----------
  var nav = document.getElementById('nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('is-scrolled', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ---------- Mobilni meni ----------
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.querySelector('.nav-menu');
  function closeMenu() {
    menu.classList.remove('is-open');
    toggle.classList.remove('is-active');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = 'Meni';
  }
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('is-open');
      toggle.classList.toggle('is-active', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? 'Zatvori' : 'Meni';
    });
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('click', function (e) {
      if (menu.classList.contains('is-open') && !menu.contains(e.target) && !toggle.contains(e.target)) closeMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) { closeMenu(); toggle.focus(); }
    });
  }

  // ---------- Hero: dioptrija pada od -5,00 do 0,00 dok se skroluje ----------
  // Prvih 40% visine ekrana skrola (isto kao margin-top na .cover u CSS-u) je 20 koraka po 0,25.
  // STEPS mora da se slaže sa brojem slika iz tools/hero-zamucenje.py.
  // Pozadina se ne zamućuje uživo: menjaju se unapred zamućene slike, pa je efekat lagan i na telefonu.
  var hero = document.getElementById('hero');
  if (hero) {
    var STEPS = 20;
    var dptVal = document.getElementById('dpt-val');
    var lastStep = -1;
    var heroTicking = false;

    var heroSrc = function (tag, step) {
      return 'images/hero/hero-' + tag + '-' + (step < 10 ? '0' : '') + step + '.webp';
    };
    // Dva sloja slike: nova slika se učita i dekodira u sloju koji se ne vidi,
    // pa tek onda pređe preko stare. Tako nema praznog kadra (treperenja) pri promeni.
    var bg = hero.querySelector('.hero-bg');
    var wash = hero.querySelector('.hero-wash');
    var layers = [0, 1].map(function () {
      var im = document.createElement('img');
      im.className = 'hero-layer'; im.alt = ''; im.decoding = 'async';
      bg.insertBefore(im, wash);
      return im;
    });
    var front = -1;
    var swapId = 0;
    var orient = function () { return window.matchMedia('(orientation: portrait)').matches ? 'p' : 'd'; };
    var showPhoto = function (step) {
      var id = ++swapId;
      var next = front === 0 ? 1 : 0;
      var im = layers[next];
      var reveal = function () {
        if (id !== swapId) return;                 // u međuvremenu je tražen drugi korak
        im.style.zIndex = '2';
        if (front >= 0) layers[front].style.zIndex = '1';
        im.classList.add('is-on');
        var prev = front;
        front = next;
        if (prev >= 0) setTimeout(function () {
          if (front !== prev) layers[prev].classList.remove('is-on');
        }, 160);
      };
      im.src = heroSrc(orient(), step);
      if (im.decode) im.decode().then(reveal, reveal); else im.onload = reveal;
    };
    var setStep = function (step) {
      if (step === lastStep) return;
      lastStep = step;
      var d = step * 0.25;
      hero.style.setProperty('--d', String(d));
      dptVal.textContent = step === 0 ? '0,00' : '\u2212' + d.toFixed(2).replace('.', ',');
      if (hero.dataset.effect !== '8') showPhoto(step);
    };

    if (reduceMotion) {
      setStep(0);
    } else {
      var renderHero = function () {
        heroTicking = false;
        var dist = hero.offsetHeight * 0.4;
        var p = dist > 0 ? Math.min(1, Math.max(0, window.scrollY / dist)) : 1;
        setStep(Math.round((1 - p) * STEPS));
      };
      var requestHero = function () {
        if (!heroTicking) { heroTicking = true; requestAnimationFrame(renderHero); }
      };
      window.addEventListener('scroll', requestHero, { passive: true });
      window.addEventListener('resize', requestHero);
      renderHero();

      // učitaj ostale nivoe zamućenja u pozadini, samo za trenutnu orijentaciju ekrana
      var preload = function () {
        if (hero.dataset.effect === '8') return; // tablica za vid ne koristi fotografije
        var tag = window.matchMedia('(orientation: portrait)').matches ? 'p' : 'd';
        for (var i = STEPS - 1; i >= 0; i--) { var im = new Image(); im.decoding = 'async'; im.src = heroSrc(tag, i); }
      };
      if ('requestIdleCallback' in window) requestIdleCallback(preload, { timeout: 2000 });
      else window.addEventListener('load', preload);
    }
  }

  // ---------- Clip-on: prekidač bez stakla / sa staklom ----------
  var clipPhoto = document.getElementById('clip-photo');
  if (clipPhoto) {
    var segBtns = document.querySelectorAll('.seg-btn');
    segBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var on = btn.getAttribute('data-clip');
        clipPhoto.setAttribute('data-on', on);
        segBtns.forEach(function (b) {
          var active = b === btn;
          b.classList.toggle('is-on', active);
          b.setAttribute('aria-pressed', String(active));
        });
      });
    });
  }

  // ---------- Reveal pri skrolu ----------
  var targets = document.querySelectorAll(
    '.h2, .wall-item, .clip-photo, .svc-list li, .story-text, .visit-block, .visit-map'
  );
  if (!reduceMotion && 'IntersectionObserver' in window) {
    targets.forEach(function (el) { el.classList.add('reveal'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        setTimeout(function () { el.classList.add('is-visible'); }, (i % 6) * 70);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
  }

  // ---------- Godina u footeru ----------
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
