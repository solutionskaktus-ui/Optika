/* ============================================
   OPTIKA VISAGE — main.js
   Minimal JS — mobile menu, scroll reveal, year
   ============================================ */

(function () {
  'use strict';

  // ---------- Mobile menu toggle ----------
  const toggle = document.querySelector('.nav-toggle');
  const menu = document.querySelector('.nav-menu');

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      const isOpen = menu.classList.toggle('is-open');
      toggle.classList.toggle('is-active');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close menu when a link is clicked
    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        menu.classList.remove('is-open');
        toggle.classList.remove('is-active');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ---------- Smooth scroll for in-page anchors (with offset for sticky nav) ----------
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#' || href.length < 2) return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      const navHeight = document.querySelector('.nav')?.offsetHeight || 0;
      const y = target.getBoundingClientRect().top + window.pageYOffset - navHeight + 1;
      window.scrollTo({ top: y, behavior: 'smooth' });
    });
  });

  // ---------- Scroll reveal animations ----------
  const revealTargets = document.querySelectorAll(
    '.section-head, .service-card, .process-list li, .review-card, .faq-item, .stat, .contact-block, .hero-card, .hero-meta'
  );

  revealTargets.forEach(function (el) {
    el.classList.add('reveal');
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry, index) {
          if (entry.isIntersecting) {
            // Small stagger for grouped items
            const delay = (index % 6) * 60;
            setTimeout(function () {
              entry.target.classList.add('is-visible');
            }, delay);
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }
    );

    revealTargets.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback for old browsers
    revealTargets.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  // ---------- Dynamic year in footer ----------
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // ---------- Pause marquee when not in view (perf) ----------
  const marquee = document.querySelector('.marquee-track');
  if (marquee && 'IntersectionObserver' in window) {
    const marqueeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        marquee.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused';
      });
    });
    marqueeObserver.observe(marquee);
  }

  // ---------- Close mobile menu on outside click ----------
  document.addEventListener('click', function (e) {
    if (!menu || !toggle) return;
    if (!menu.classList.contains('is-open')) return;
    if (menu.contains(e.target) || toggle.contains(e.target)) return;
    menu.classList.remove('is-open');
    toggle.classList.remove('is-active');
    toggle.setAttribute('aria-expanded', 'false');
  });

})();
