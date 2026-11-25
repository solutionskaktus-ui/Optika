/* ============================================
   OPTIKA VISAGE, main.js
   Meni, prvi ekran početne, reveal, godina
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

  // ---------- Početna: prvi ekran i prelaz "Fokus" ----------
  // Dok se skroluje, prvi ekran se zamuti i blago udalji (kao kroz pogrešnu dioptriju),
  // a zid sa okvirima ispod se izoštri. Ko je isključio animacije, dobija običan skrol.
  var nh = document.getElementById('pocetna');
  if (nh) {
    try {
      var danNh = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Belgrade', weekday: 'short' }).format(new Date());
      if (['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].indexOf(danNh) > -1) document.getElementById('pocetna-rd').className = 'nh-danas';
      if (danNh === 'Sat') document.getElementById('pocetna-sb').className = 'nh-danas';
    } catch (e) {}

    var nhCover = document.querySelector('.nh ~ .cover');
    var nhNext = nhCover && nhCover.firstElementChild;
    document.getElementById('pocetna-dalje').addEventListener('click', function () {
      if (!nhCover) return;
      window.scrollTo({ top: nhCover.offsetTop, behavior: reduceMotion ? 'auto' : 'smooth' });
    });

    if (!reduceMotion && nhNext) {
      var nhClamp = function (x, lo, hi) { return Math.min(hi, Math.max(lo, x)); };
      var nhTicking = false;
      var nhUpdate = function () {
        nhTicking = false;
        var k = nhClamp(window.scrollY / window.innerHeight, 0, 1);
        var blur = k * 14, op = nhClamp(1 - k * 1.45, 0, 1);
        nh.style.filter = blur > .2 ? 'blur(' + blur.toFixed(1) + 'px)' : '';
        nh.style.transform = k > 0 ? 'scale(' + (1 - k * .05).toFixed(4) + ')' : '';
        nh.style.opacity = op.toFixed(3);
        nh.style.visibility = op <= 0 ? 'hidden' : '';
        var g = (1 - nhClamp(k * 1.25, 0, 1)) * 14;
        nhNext.style.filter = g > .2 ? 'blur(' + g.toFixed(1) + 'px)' : '';
        nhNext.style.opacity = nhClamp(.15 + k * 1.3, 0, 1).toFixed(3);
      };
      window.addEventListener('scroll', function () { if (!nhTicking) { nhTicking = true; requestAnimationFrame(nhUpdate); } }, { passive: true });
      window.addEventListener('resize', nhUpdate);
      nhUpdate();
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

  // ---------- Katalog: filter okvira ----------
  var katalog = document.getElementById('katalog');
  if (katalog) {
    var fBtns = document.querySelectorAll('[data-filter]');
    var applyFilter = function (f) {
      katalog.querySelectorAll('.wall-item, .gal-model').forEach(function (it) {
        var tags = (it.getAttribute('data-filteri') || '').split(' ');
        it.classList.toggle('is-hidden', f !== 'svi' && tags.indexOf(f) === -1);
      });
      fBtns.forEach(function (b) {
        var on = b.getAttribute('data-filter') === f;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-pressed', String(on));
      });
    };
    fBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        applyFilter(f);
        if (history.replaceState) history.replaceState(null, '', f === 'svi' ? location.pathname : '#' + f);
      });
    });
    var h = location.hash.slice(1);
    if (h && document.querySelector('[data-filter="' + h + '"]')) applyFilter(h);
  }

  // ---------- Galerija: fotografija preko celog ekrana ----------
  var lb = document.getElementById('lb');
  if (lb && typeof lb.showModal === 'function') {
    var lbImg = lb.querySelector('.lb-img');
    var lbCap = lb.querySelector('.lb-cap');
    var lbCount = lb.querySelector('.lb-count');
    var lbPrev = lb.querySelector('.lb-prev');
    var lbNext = lb.querySelector('.lb-next');
    var group = [], idx = 0, opener = null;
    var preload = function (a) { if (a) { var im = new Image(); im.src = a.getAttribute('href'); } };
    var show = function (i) {
      idx = (i + group.length) % group.length;
      var a = group[idx];
      var cap = a.getAttribute('data-cap') || '';
      lbImg.src = a.getAttribute('href');
      lbImg.alt = cap;
      lbCap.textContent = cap;
      var multi = group.length > 1;
      lbCount.textContent = multi ? (idx + 1) + ' / ' + group.length : '';
      lbPrev.hidden = !multi;
      lbNext.hidden = !multi;
      if (multi) { preload(group[(idx + 1) % group.length]); preload(group[(idx - 1 + group.length) % group.length]); }
    };
    document.querySelectorAll('[data-lb]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        group = Array.prototype.slice.call(document.querySelectorAll('[data-lb="' + a.getAttribute('data-lb') + '"]'));
        opener = a;
        show(group.indexOf(a));
        document.documentElement.classList.add('lb-open');
        lb.showModal();
      });
    });
    lbPrev.addEventListener('click', function () { show(idx - 1); });
    lbNext.addEventListener('click', function () { show(idx + 1); });
    var cleanup = function () {
      if (!document.documentElement.classList.contains('lb-open')) return;
      document.documentElement.classList.remove('lb-open');
      lbImg.removeAttribute('src');
      if (opener) opener.focus({ preventScroll: true });
    };
    var closeLb = function () { if (lb.open) lb.close(); cleanup(); };
    lb.querySelector('.lb-close').addEventListener('click', closeLb);
    lb.addEventListener('close', cleanup); // Esc zatvara sam dijalog
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(idx - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); show(idx + 1); }
    });
    // klik pored fotografije zatvara
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb-fig')) closeLb(); });
    // prevlačenje prstom levo/desno
    var x0 = null, y0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (group.length > 1 && Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  // ---------- Futrole: sličice na kartici i prozor za jednu futrolu ----------
  var fd = document.getElementById('fd');
  var futEl = document.getElementById('fut-data');
  if (fd && futEl && typeof fd.showModal === 'function') {
    var FUT = JSON.parse(futEl.textContent);
    var fdImg = fd.querySelector('.fd-img'), fdThumbs = fd.querySelector('.fd-thumbs'), fdColors = fd.querySelector('.fd-colors');
    var fdPrev = fd.querySelector('.fd-prev'), fdNext = fd.querySelector('.fd-next');
    var fdCur = null, fdIdx = 0, fdOpener = null, fdPushed = false;
    var srcset = function (b) { return b + '-800.webp 800w, ' + b + '-1600.webp 1600w'; };
    var esc = function (t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); };

    // kartica: prelaz mišem preko sličice menja veliku fotografiju
    document.querySelectorAll('.fut-item').forEach(function (card) {
      var main = card.querySelector('.fut-main img'), f = FUT.futrole[card.getAttribute('data-fut')];
      var mini = card.querySelectorAll('.fut-thumbs img');
      if (!f || !main) return;
      var pokazi = function (i) {
        main.srcset = srcset(f.slike[i]); main.src = f.slike[i] + '-800.webp';
        mini.forEach(function (m, j) { m.classList.toggle('is-on', j === i); });
      };
      if (mini.length) mini[0].classList.add('is-on');
      mini.forEach(function (m, j) { m.addEventListener('mouseenter', function () { pokazi(j); }); });
      card.addEventListener('mouseleave', function () { if (mini.length) pokazi(0); });
      card.addEventListener('click', function (e) { e.preventDefault(); fdOpener = card; openFd(card.getAttribute('data-fut'), 'push'); });
    });

    var showFd = function (i) {
      var f = FUT.futrole[fdCur], n = f.slike.length;
      fdIdx = (i + n) % n;
      var b = f.slike[fdIdx];
      fdImg.srcset = srcset(b); fdImg.sizes = '(min-width: 900px) 600px, 100vw'; fdImg.src = b + '-1600.webp';
      fdImg.alt = f.ime + ', ' + f.pogledi[fdIdx];
      fdThumbs.querySelectorAll('button').forEach(function (t, j) { t.setAttribute('aria-current', j === fdIdx ? 'true' : 'false'); });
      fdPrev.hidden = fdNext.hidden = n < 2;
      if (n > 1) { [fdIdx + 1, fdIdx - 1].forEach(function (k) { var im = new Image(); im.src = f.slike[(k + n) % n] + '-1600.webp'; }); }
    };

    var openFd = function (id, hist) {
      var f = FUT.futrole[id];
      if (!f) return;
      fdCur = id;
      fd.querySelector('.fd-title').textContent = f.ime;
      fd.querySelector('.fd-opis').textContent = f.opis;
      fdThumbs.innerHTML = f.slike.length < 2 ? '' : f.slike.map(function (b, j) {
        return '<button type="button" aria-label="' + esc(f.pogledi[j]) + '"><img src="' + b + '-240.webp" alt="" width="240" height="180"></button>';
      }).join('');
      fdThumbs.querySelectorAll('button').forEach(function (t, j) { t.addEventListener('click', function () { showFd(j); }); });
      fdColors.innerHTML = FUT.modeli[f.model].map(function (cid) {
        var c = FUT.futrole[cid];
        return '<button type="button" data-id="' + cid + '" aria-current="' + (cid === id) + '"><img src="' + c.slike[0] + '-240.webp" alt="" width="240" height="180"><span>' + esc(c.boja) + '</span></button>';
      }).join('');
      fdColors.querySelectorAll('button').forEach(function (t) { t.addEventListener('click', function () { openFd(t.getAttribute('data-id'), 'replace'); }); });
      showFd(0);
      if (!fd.open) { document.documentElement.classList.add('fd-open'); fd.showModal(); }
      fd.scrollTop = 0;
      if (hist === 'push') {
        // novi korak u istoriji, da dugme Nazad na telefonu zatvori prozor umesto da napusti stranu
        var n0 = history.length;
        history.pushState({ fd: id }, '', '#' + id);
        fdPushed = history.length > n0;
      } else if (hist === 'replace') history.replaceState(fdPushed ? { fd: id } : null, '', '#' + id);
    };
    var hideFd = function () {
      if (fd.open) fd.close();
      document.documentElement.classList.remove('fd-open');
      if (FUT.futrole[location.hash.slice(1)]) history.replaceState(null, '', location.pathname + location.search);
      fdCur = null; fdPushed = false;
      if (fdOpener) fdOpener.focus({ preventScroll: true });
    };
    // zatvaranje: dugme Nazad na telefonu, Esc, dugme Zatvori i klik pored panela rade isto
    var closeFd = function () { if (fdPushed && history.state && history.state.fd) history.back(); else hideFd(); };
    window.addEventListener('popstate', function () {
      var id = location.hash.slice(1);
      fdPushed = !!(history.state && history.state.fd);
      if (FUT.futrole[id]) openFd(id, 'none'); else if (fd.open) hideFd();
    });
    fd.querySelector('.fd-close').addEventListener('click', closeFd);
    fd.addEventListener('cancel', function (e) { e.preventDefault(); closeFd(); });
    fd.addEventListener('click', function (e) { if (e.target === fd) closeFd(); });
    fdPrev.addEventListener('click', function () { showFd(fdIdx - 1); });
    fdNext.addEventListener('click', function () { showFd(fdIdx + 1); });
    fd.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); showFd(fdIdx - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); showFd(fdIdx + 1); }
    });
    var fx = null, fy = null, fdMain = fd.querySelector('.fd-main');
    fdMain.addEventListener('touchstart', function (e) { fx = e.touches[0].clientX; fy = e.touches[0].clientY; }, { passive: true });
    fdMain.addEventListener('touchend', function (e) {
      if (fx === null) return;
      var dx = e.changedTouches[0].clientX - fx, dy = e.changedTouches[0].clientY - fy;
      fx = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) showFd(fdIdx + (dx < 0 ? 1 : -1));
    });
    // adresa sa nazivom futrole (#nera-ljubicasta) odmah otvara tu futrolu
    if (FUT.futrole[location.hash.slice(1)]) openFd(location.hash.slice(1), 'replace');
  }

  // ---------- Stranica modela: galerija ----------
  var gImg = document.querySelector('.gallery-img');
  if (gImg) {
    var thumbs = document.querySelectorAll('.thumb');
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () {
        var base = t.getAttribute('data-src');
        gImg.src = base + '-800.webp';
        gImg.srcset = base + '-800.webp 800w, ' + base + '-1600.webp 1600w';
        gImg.alt = t.getAttribute('data-alt');
        thumbs.forEach(function (x) {
          x.classList.toggle('is-on', x === t);
          x.setAttribute('aria-pressed', String(x === t));
        });
      });
    });
  }

  // ---------- Korpa ----------
  // Korpa se čuva u pregledaču posetioca (localStorage). Porudžbina se šalje preko FormSubmit-a
  // na email iz data-endpoint na formi (/korpa/).
  var KEY = 'visage-korpa';
  var readCart = function () {
    try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; }
  };
  var writeCart = function (items) {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* privatni prozor: korpa radi do zatvaranja stranice */ }
    memCart = items;
    updateBadge();
  };
  var memCart = readCart();
  var cartItems = function () { var v = readCart(); return v.length || !memCart.length ? v : memCart; };
  var rsd = function (n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' RSD'; };
  var updateBadge = function () {
    var n = cartItems().length;
    document.querySelectorAll('.nav-cart').forEach(function (el) {
      el.hidden = n === 0;
      var c = el.querySelector('.nav-cart-n'); if (c) c.textContent = String(n);
      el.setAttribute('aria-label', 'Korpa, ' + n + (n === 1 ? ' okvir' : ' okvira'));
    });
  };
  updateBadge();

  document.querySelectorAll('.buy').forEach(function (box) {
    var btn = box.querySelector('.buy-add');
    var done = box.querySelector('.buy-done');
    btn.addEventListener('click', function () {
      var items = cartItems();
      items.push({
        id: Date.now() + '-' + Math.random().toString(36).slice(2, 7),
        slug: box.getAttribute('data-slug'), ime: box.getAttribute('data-ime'),
        cena: parseInt(box.getAttribute('data-cena'), 10) || 0, slika: box.getAttribute('data-slika'),
        url: location.pathname, staklo: box.querySelector('.buy-staklo').value
      });
      writeCart(items);
      done.hidden = false;
      btn.textContent = 'Dodaj još jedan';
      if (typeof window.gtag === 'function') window.gtag('event', 'add_to_cart', { item_name: box.getAttribute('data-ime') });
    });
  });

  var order = document.getElementById('order');
  if (order) {
    var list = document.getElementById('cart-list');
    var tpl = document.getElementById('cart-item');
    var empty = document.getElementById('cart-empty');
    var done = document.getElementById('order-done');
    var err = document.getElementById('order-error');
    var rx = document.getElementById('rx');
    var render = function () {
      var items = cartItems();
      list.innerHTML = '';
      order.hidden = items.length === 0;
      empty.hidden = items.length !== 0;
      var total = 0;
      items.forEach(function (it) {
        total += it.cena || 0;
        var li = tpl.content.firstElementChild.cloneNode(true);
        li.querySelector('.cart-img').src = it.slika;
        var a = li.querySelector('.cart-name'); a.textContent = it.ime; a.href = it.url;
        li.querySelector('.cart-price').textContent = it.cena ? rsd(it.cena) : 'Cena na upit';
        var sel = li.querySelector('.cart-staklo'); sel.value = it.staklo;
        sel.addEventListener('change', function () {
          var all = cartItems(); all.forEach(function (x) { if (x.id === it.id) x.staklo = sel.value; }); writeCart(all);
        });
        li.querySelector('.cart-remove').addEventListener('click', function () {
          writeCart(cartItems().filter(function (x) { return x.id !== it.id; })); render();
        });
        list.appendChild(li);
      });
      document.getElementById('cart-total').textContent = rsd(total);
    };
    render();

    order.querySelectorAll('input[name="dioptrija_nacin"]').forEach(function (r) {
      r.addEventListener('change', function () { rx.hidden = r.value !== 'Upisaću dioptriju' || !r.checked; });
    });

    var shipAdresa = document.getElementById('ship-adresa');
    var shipRadnja = document.getElementById('ship-radnja');
    var isDostava = function () {
      var c = order.querySelector('input[name="isporuka"]:checked');
      return !c || c.value === 'Dostava na adresu';
    };
    var syncShip = function () { var d = isDostava(); shipAdresa.hidden = !d; shipRadnja.hidden = d; };
    order.querySelectorAll('input[name="isporuka"]').forEach(function (r) { r.addEventListener('change', syncShip); });
    syncShip();

    order.addEventListener('submit', function (e) {
      e.preventDefault();
      err.hidden = true;
      var f = new FormData(order);
      if (f.get('_honey')) return;
      var missing = [];
      if (!String(f.get('ime') || '').trim()) missing.push('ime i prezime');
      if (!String(f.get('telefon') || '').trim()) missing.push('telefon');
      var dostava = isDostava();
      if (dostava && !String(f.get('adresa') || '').trim()) missing.push('adresa');
      if (dostava && !String(f.get('naselje') || '').trim()) missing.push('opština ili naselje');
      if (!f.get('saglasnost')) missing.push('saglasnost');
      if (missing.length) { err.textContent = 'Popunite: ' + missing.join(', ') + '.'; err.hidden = false; return; }
      var items = cartItems();
      var total = 0;
      var lines = items.map(function (it, i) { total += it.cena || 0; return (i + 1) + '. ' + it.ime + ' (' + (it.cena ? rsd(it.cena) : 'cena na upit') + '), staklo: ' + it.staklo; });
      var nacin = f.get('dioptrija_nacin');
      var v = function (k) { return String(f.get(k) || '').trim() || '-'; };
      var data = {
        _subject: 'Nova porudžbina sa sajta: ' + f.get('ime'),
        _template: 'table',
        _captcha: 'false',
        'Ime i prezime': f.get('ime'), 'Telefon': f.get('telefon'), 'Email': f.get('email') || '-',
        'Okviri': lines.join('\n'), 'Okviri ukupno': rsd(total), 'Dioptrija': nacin
      };
      if (nacin === 'Upisaću dioptriju') {
        data['Desno oko (OD)'] = 'SPH ' + v('od_sph') + ', CYL ' + v('od_cyl') + ', AX ' + v('od_ax');
        data['Levo oko (OS)'] = 'SPH ' + v('os_sph') + ', CYL ' + v('os_cyl') + ', AX ' + v('os_ax');
        data['PD'] = v('pd'); data['ADD'] = v('add');
      }
      if (dostava) {
        data['Isporuka'] = 'Dostava na adresu, pouzeće (gotovina)';
        data['Adresa'] = v('adresa') + ', ' + v('naselje') + ', Beograd';
      } else {
        data['Isporuka'] = 'Preuzimanje u radnji, TC Medaković 3';
      }
      data['Napomena'] = v('napomena');
      if (f.get('email')) data._replyto = f.get('email');
      var btn = order.querySelector('.order-submit');
      btn.disabled = true; btn.textContent = 'Šaljem...';
      fetch(order.getAttribute('data-endpoint'), {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data)
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok || String(res.j && res.j.success) === 'false') throw new Error(res.j && res.j.message || 'greška');
          writeCart([]);
          order.hidden = true; done.hidden = false;
          if (typeof window.gtag === 'function') window.gtag('event', 'porudzbina_poslata', { value: total, currency: 'RSD' });
          window.scrollTo(0, 0);
        })
        .catch(function () {
          err.innerHTML = 'Porudžbina nije poslata. Pokušajte ponovo ili nam pišite na <a class="text-link" href="viber://chat?number=%2B381603175264">Viber</a> ili pozovite <a class="text-link" href="tel:+381603175264">060 3175264</a>.';
          err.hidden = false;
        })
        .then(function () { btn.disabled = false; btn.textContent = 'Pošalji porudžbinu'; });
    });
  }

  // ---------- Reveal pri skrolu ----------
  var targets = document.querySelectorAll(
    '.h2, .wall-item, .clip-photo, .svc-list li, .story-text, .visit-block, .visit-map, .link-card, .photo, .cta-panel'
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
