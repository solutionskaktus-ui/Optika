"""
Generator podstranica sajta Optika Visage.

Pravi: okviri/, usluge/ (pregled i 4 usluge), o-nama/, kontakt/, pitanja/, korpa/,
zid sa okvirima na početnoj i sitemap.xml. Ostatak početne (index.html) se uređuje ručno.
Sa PRODAVNICA = True okviri/ je katalog sa stranicom za svaki model i korpom;
sa PRODAVNICA = False okviri/ je galerija, a adrese modela i korpe vode na nju.

Podaci o okvirima su u data/okviri.json, pitanja u data/pitanja.json.
Posle izmene teksta ili dodavanja okvira pokrenuti iz korena repoa:
    python3 tools/stranice.py
"""
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://optikavisage.com'
TODAY = date.today().isoformat()
TEL = '+381603175264'
TEL_TXT = '060 3175264'
VIBER = 'viber://chat?number=%2B381603175264'
MAPS_DIR = 'https://www.google.com/maps/dir/?api=1&amp;destination=44.7727127,20.5079659'
MAPS_REVIEWS = ('https://www.google.com/maps/place/Optika+Visage/@44.7726675,20.5074835,20.25z/'
                'data=!4m6!3m5!1s0x475a716f32d1f9cb:0xbde644c80bc34fa!8m2!3d44.7727127!4d20.5079659')
ARROW = ''

# Prodavnica: korpa, cene okvira i posebna stranica za svaki model.
# Kada je isključena, /okviri/ je galerija sa svim fotografijama, a adrese
# modela (/okviri/<slug>/) i korpe vode na galeriju. Puna verzija je na grani `prodavnica`.
PRODAVNICA = False

OKVIRI =json.loads((ROOT / 'data' / 'okviri.json').read_text(encoding='utf-8'))['okviri']
PITANJA = json.loads((ROOT / 'data' / 'pitanja.json').read_text(encoding='utf-8'))['pitanja']

POGLED = {
    'spreda': 'spreda', 'spreda-2': 'spreda', 'poluprofil': 'iz poluprofila', 'profil': 'sa strane',
    'sa-strane': 'sa strane', 'otpozadi': 'otpozadi', 'sklopljen': 'sklopljen',
    'clip-on-spreda': 'sa clip-on staklom, spreda', 'clip-on-poluprofil': 'sa clip-on staklom, iz poluprofila',
    'clip-on-profil': 'sa clip-on staklom, sa strane', 'clip-on-pored': 'sa clip-on staklom pored okvira',
    'clip-on-podignut': 'sa podignutim clip-on staklom', 'futrola': 'na Tony Morgan futroli',
    'futrola-otvorena-1': 'u otvorenoj Tony Morgan futroli sa krpicom',
    'futrola-otvorena-2': 'u otvorenoj Tony Morgan futroli',
    'futrola-otvorena-3': 'ispred otvorene Tony Morgan futrole',
    'futrola-otvorena-4': 'na krpici ispred Tony Morgan futrole',
}


def img(base, alt, w=800, h=600, sizes='100vw', cls='', lazy=True):
    a = f' class="{cls}"' if cls else ''
    lz = ' loading="lazy"' if lazy else ''
    return (f'<img{a} src="{base}-800.webp" srcset="{base}-800.webp 800w, {base}-1600.webp 1600w" '
            f'sizes="{sizes}" alt="{escape(alt)}" width="{w}" height="{h}"{lz} decoding="async">')


def okvir_img_base(o, view):
    f = o.get('slike', o['slug'])
    return f'/images/okviri/{f}/{f}-{view}'


def rsd(n):
    return f'{n:,.0f}'.replace(',', '.') + ' RSD'


STAKLA = json.loads((ROOT / 'data' / 'okviri.json').read_text(encoding='utf-8')).get('stakla', [])
FORM_EMAIL = 'optikavisage@gmail.com'
CART_SVG = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h15l-1.5 9h-12z"/>'
            '<path d="M6 7 5 3H2"/><circle cx="9" cy="20" r="1.3"/><circle cx="18" cy="20" r="1.3"/></svg>')


def kartica(o, sizes='(max-width: 1020px) 50vw, 25vw'):
    if o.get('par'):
        main = img(okvir_img_base(o, 'uporedjenje-bez'), o['ime'], 800, 500, sizes)
        alt = (f'<img class="wall-alt" src="{okvir_img_base(o, "uporedjenje-sa")}-800.webp" '
               f'alt="" width="800" height="500" loading="lazy" decoding="async">')
    else:
        main = img(okvir_img_base(o, o.get('kartica', 'spreda')), o['ime'], 800, 600, sizes)
        alt = ''
    href = f'/okviri/{o["slug"]}/' if PRODAVNICA else f'/okviri/#{o["slug"]}'
    return (f'        <li class="wall-item" data-filteri="{" ".join(o["filteri"])}">\n'
            f'          <a href="{href}">\n'
            f'            <span class="wall-img wall-img--studio">{main}{alt}</span>\n'
            f'            <span class="wall-name">{escape(o["kratko"])}</span>\n'
            f'            <span class="wall-cat">{escape(o["tip"])}</span>\n'
            + (f'            <span class="wall-price">{rsd(o["cena"])}</span>\n' if PRODAVNICA and o.get('cena') else '')
            + f'          </a>\n        </li>')


# ---------------------------------------------------------------- okvir stranice

def head(title, desc, path, schema=None, og_image='/images/og-image-visage-optika.jpg'):
    sch = ''
    for s in (schema or []):
        sch += '<script type="application/ld+json">\n' + json.dumps(s, ensure_ascii=False, indent=2) + '\n</script>\n'
    return f'''<!DOCTYPE html>
<html lang="sr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#FAF7FB">

<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-D939MT9X6K"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-D939MT9X6K');
</script>

<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{SITE}{path}">

<meta property="og:type" content="website">
<meta property="og:locale" content="sr_RS">
<meta property="og:site_name" content="Optika Visage">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" type="image/x-icon" href="/favicons/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicons/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicons/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rethink+Sans:ital,wght@0,400..800;1,400..800&family=Barlow+Condensed:wght@500;600&display=swap" rel="stylesheet">

<link rel="stylesheet" href="/css/styles.css">
<script>document.documentElement.classList.add('js');</script>
{sch}</head>
<body class="sub">

<a class="skip-link" href="#sadrzaj">Preskoči na sadržaj</a>
'''


def nav(active):
    def link(href, label, key):
        cur = ' aria-current="page"' if key == active else ''
        return f'      <a href="{href}"{cur}>{label}</a>'
    return f'''
<header class="nav" id="nav">
  <div class="container nav-inner">
    <a href="/" class="nav-logo" aria-label="Visage Optika, početna">
      <img src="/images/visage-logo-mark.png" alt="" width="34" height="21">
      <span class="logo-wordmark"><strong>VISAGE</strong>OPTIKA</span>
    </a>
    <nav class="nav-menu" id="nav-menu" aria-label="Glavna navigacija">
{link("/okviri/", "Okviri", "okviri")}
{link("/usluge/", "Usluge", "usluge")}
{link("/o-nama/", "O nama", "o-nama")}
{link("/kontakt/", "Kontakt", "kontakt")}
      <a href="tel:{TEL}" class="nav-tel">{TEL_TXT}</a>
      <a href="{VIBER}" class="btn btn-primary nav-cta">Zakažite proveru</a>
    </nav>
{f'    <a href="/korpa/" class="nav-cart" aria-label="Korpa" hidden>{CART_SVG}<span class="nav-cart-n">0</span></a>' + chr(10) if PRODAVNICA else ''}    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-menu">Meni</button>
  </div>
</header>
'''


FOOTER = f'''
<footer class="footer">
  <div class="container footer-inner">
    <a href="/" class="nav-logo" aria-label="Visage Optika, početna">
      <img src="/images/visage-logo-mark.png" alt="" width="34" height="21">
      <span class="logo-wordmark"><strong>VISAGE</strong>OPTIKA</span>
    </a>
    <nav class="footer-links" aria-label="Stranice">
      <a href="/okviri/">Okviri</a>
      <a href="/usluge/">Usluge</a>
      <a href="/o-nama/">O nama</a>
      <a href="/kontakt/">Kontakt</a>
      <a href="/pitanja/">Pitanja</a>
      <a href="https://www.instagram.com/optika_visage/" rel="me noopener" target="_blank">Instagram</a>
      <a href="https://www.facebook.com/optikavisage" rel="me noopener" target="_blank">Facebook</a>
    </nav>
    <p class="footer-contact"><span>Braće Srnić 23a, TC Medaković 3, lokal 45, 11050 Beograd</span><a href="tel:{TEL}">{TEL_TXT}</a><a href="mailto:optikavisage@gmail.com">optikavisage@gmail.com</a></p>
    <p class="footer-legal"><span>© <span id="year">2026</span> Optika Visage</span><span>PIB 112372621</span><span>MB 21660418</span></p>
  </div>
</footer>

<script src="/js/main.js"></script>

</body>
</html>
'''


def breadcrumbs(items):
    """items: [(naziv, putanja)], poslednji je trenutna stranica."""
    html = '<ol class="crumbs">'
    for i, (name, path) in enumerate(items):
        if i == len(items) - 1:
            html += f'<li aria-current="page">{escape(name)}</li>'
        else:
            html += f'<li><a href="{path}">{escape(name)}</a></li>'
    html += '</ol>'
    schema = {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + p}
                            for i, (n, p) in enumerate(items)],
    }
    return html, schema


def page_head(crumbs_html, title, lead=''):
    lead_html = f'\n      <p class="page-lead">{lead}</p>' if lead else ''
    return f'''
  <section class="page-head">
    <div class="container">
      <nav aria-label="Putanja">{crumbs_html}</nav>
      <h1 class="page-title">{title}</h1>{lead_html}
    </div>
  </section>
'''


def cta_panel(title='Probajte okvire u radnji', text='Zakazivanje nije obavezno, ali ako ne želite da čekate, pozovite ili pišite na Viber.'):
    return f'''
  <section class="section cta">
    <div class="container">
      <div class="cta-panel">
        <h2 class="h2">{title}</h2>
        <p class="lead center">{text}</p>
        <div class="cta-actions">
          <a href="{VIBER}" class="btn btn-primary">Pišite na Viber</a>
          <a href="tel:{TEL}" class="btn btn-line">Pozovite {TEL_TXT}</a>
        </div>
        <p class="cta-addr">Braće Srnić 23a, TC Medaković 3, srednji ulaz, lokal 45</p>
      </div>
    </div>
  </section>
'''


def write(path, html):
    out = ROOT / path.strip('/') / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return path


def preusmeri(path, target, title):
    """Mala stranica koja staru adresu odmah vodi na novu (GitHub Pages nema preusmeravanja)."""
    write(path, f'''<!DOCTYPE html>
<html lang="sr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)} | Optika Visage</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{SITE}/okviri/">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace('{target}');</script>
</head>
<body>
<p><a href="{target}">{escape(title)}</a></p>
</body>
</html>
''')


# ---------------------------------------------------------------- galerija (bez prodavnice)

LB_SVG = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>')
LIGHTBOX = f'''
<dialog class="lb" id="lb" aria-label="Fotografija">
  <div class="lb-top">
    <p class="lb-count" aria-live="polite"></p>
    <button type="button" class="btn btn-line lb-close">Zatvori</button>
  </div>
  <figure class="lb-fig">
    <img class="lb-img" alt="">
    <figcaption class="lb-cap"></figcaption>
  </figure>
  <div class="lb-nav">
    <button type="button" class="lb-btn lb-prev" aria-label="Prethodna fotografija">{LB_SVG.format(d="m15 5-7 7 7 7")}</button>
    <button type="button" class="lb-btn lb-next" aria-label="Sledeća fotografija">{LB_SVG.format(d="m9 5 7 7-7 7")}</button>
  </div>
</dialog>
'''


def gal_model(o):
    views = o.get('galerija', o['pogledi'])
    items = ''
    for i, v in enumerate(views):
        b = okvir_img_base(o, v)
        cap = f'{o["ime"]}, {POGLED.get(v, v)}'
        sizes = '(max-width: 759px) 100vw, 600px' if i == 0 else '(max-width: 759px) 50vw, 300px'
        items += (f'\n          <li><a class="gal-item" href="{b}-1600.webp" data-lb="{o["slug"]}" data-cap="{escape(cap)}">'
                  f'<img src="{b}-800.webp" srcset="{b}-800.webp 800w, {b}-1600.webp 1600w" sizes="{sizes}" '
                  f'alt="{escape(cap)}" width="800" height="600" loading="lazy" decoding="async"></a></li>')
    one = ' gal-grid--1' if len(views) == 1 else ''
    return f'''
    <article class="gal-model" id="{o["slug"]}" data-filteri="{" ".join(o["filteri"])}" aria-labelledby="{o["slug"]}-ime">
      <div class="container">
        <h2 class="gal-name" id="{o["slug"]}-ime">{escape(o["ime"])}</h2>
        <p class="gal-sub">{escape(o.get("podnaslov", o["tip"]))}</p>
        <ul class="gal-grid{one}">{items}
        </ul>
        <p class="gal-desc">{escape(o["opis"])}</p>
        <p class="gal-ask"><a class="text-link" href="{VIBER}">Pitajte za ovaj okvir na Viberu</a></p>
      </div>
    </article>'''


def build_galerija():
    cr, cs = breadcrumbs([('Početna', '/'), ('Okviri', '/okviri/')])
    n_clip = sum('clip-on' in o['filteri'] for o in OKVIRI)
    n_met = sum('metalni' in o['filteri'] for o in OKVIRI)
    models = '\n'.join(gal_model(o) for o in OKVIRI)
    photos = ''
    for f, a, w, h in FOTO_GALERIJA:
        b = f'/images/radnja/galerija/{f}'
        w2 = 1600 if w > h else 1200
        photos += (f'\n        <a class="radnja-item" href="{b}-1600.webp" data-lb="radnja" data-cap="{escape(a)}">'
                   f'<img src="{b}-800.webp" srcset="{b}-800.webp 800w, {b}-1600.webp {w2}w" '
                   f'sizes="(max-width: 759px) 50vw, 400px" alt="{escape(a)}" width="{w}" height="{h}" loading="lazy" decoding="async"></a>')
    html = head('Galerija okvira za naočare | Optika Visage, Voždovac',
                'Fotografije okvira iz Optike Visage na Medakoviću: Tony Morgan i Kubik clip-on okviri, William Morris i Diva trend. U radnji ima još mnogo modela.',
                '/okviri/', [cs])
    html += nav('okviri') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Galerija okvira',
                      'Deo okvira sa našeg zida, sa svim fotografijama. U radnji ima još mnogo modela, pa svratite da ih probate.')
    html += f'''
  <section class="gal" aria-label="Okviri">
    <div class="container">
      <div class="seg seg--filter" role="group" aria-label="Filter okvira">
        <button type="button" class="seg-btn is-on" data-filter="svi" aria-pressed="true">Svi <span class="seg-n">{len(OKVIRI)}</span></button>
        <button type="button" class="seg-btn" data-filter="clip-on" aria-pressed="false">Clip-on <span class="seg-n">{n_clip}</span></button>
        <button type="button" class="seg-btn" data-filter="metalni" aria-pressed="false">Metalni <span class="seg-n">{n_met}</span></button>
      </div>
      <p class="katalog-note">Clip-on je dodatno sunčano staklo koje se kači na okvir sa dioptrijom. Imaju ga svi Tony Morgan okviri i Kubik.</p>
    </div>
    <div class="gal-list" id="katalog">
{models}
    </div>
  </section>

  <section class="section gal-radnja" id="radnja" aria-labelledby="radnja-title">
    <div class="container">
      <h2 class="h2" id="radnja-title">U našoj radnji</h2>
      <div class="radnja-grid">{photos}
      </div>
    </div>
  </section>
'''
    html += cta_panel('Još mnogo modela u radnji',
                      'Na sajtu je samo deo ponude. Svratite da probate okvire, a ako ne želite da čekate, pozovite ili pišite na Viber.')
    html += '\n</main>\n' + LIGHTBOX + FOOTER
    return write('/okviri/', html)


def build_katalog():
    if not PRODAVNICA:
        return build_galerija()
    cr, cs = breadcrumbs([('Početna', '/'), ('Okviri', '/okviri/')])
    n_clip = sum('clip-on' in o['filteri'] for o in OKVIRI)
    n_met = sum('metalni' in o['filteri'] for o in OKVIRI)
    cards = '\n'.join(kartica(o) for o in OKVIRI)
    items = {'@context': 'https://schema.org', '@type': 'ItemList',
             'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}/okviri/{o["slug"]}/',
                                  'name': o['ime']} for i, o in enumerate(OKVIRI)]}
    html = head('Okviri za naočare i clip-on okviri | Optika Visage, Voždovac',
                'Okviri za dioptrijske naočare u Optici Visage na Medakoviću: Tony Morgan i Kubik clip-on okviri, William Morris i Diva trend. Probajte ih u radnji.',
                '/okviri/', [cs, items])
    html += nav('okviri') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Okviri za naočare',
                      'Izbor okvira sa našeg zida. Svaki možete probati u radnji, a na zidu ima još mnogo modela.')
    html += f'''
  <section class="section wall wall--katalog" aria-label="Okviri">
    <div class="container">
      <div class="seg seg--filter" role="group" aria-label="Filter okvira">
        <button type="button" class="seg-btn is-on" data-filter="svi" aria-pressed="true">Svi <span class="seg-n">{len(OKVIRI)}</span></button>
        <button type="button" class="seg-btn" data-filter="clip-on" aria-pressed="false">Clip-on <span class="seg-n">{n_clip}</span></button>
        <button type="button" class="seg-btn" data-filter="metalni" aria-pressed="false">Metalni <span class="seg-n">{n_met}</span></button>
      </div>
      <ul class="wall-grid" id="katalog">
{cards}
      </ul>
      <p class="katalog-note">Clip-on je dodatno sunčano staklo koje se kači na okvir sa dioptrijom. Imaju ga svi Tony Morgan okviri i Kubik. Cene okvira kreću se od 1.000 do 20.000 RSD.</p>
    </div>
  </section>
'''
    html += cta_panel()
    html += '\n</main>\n' + FOOTER
    return write('/okviri/', html)


def build_model(o):
    path = f'/okviri/{o["slug"]}/'
    if not PRODAVNICA:
        preusmeri(path, f'/okviri/#{o["slug"]}', o['ime'])
        return None
    cr, cs = breadcrumbs([('Početna', '/'), ('Okviri', '/okviri/'), (o['kratko'], path)])
    views = o['pogledi']
    first = okvir_img_base(o, views[0])
    main_alt = f'{o["ime"]}, {POGLED.get(views[0], views[0])}'
    thumbs = ''
    for i, v in enumerate(views):
        b = okvir_img_base(o, v)
        alt = f'{o["ime"]}, {POGLED.get(v, v)}'
        on = ' is-on' if i == 0 else ''
        thumbs += (f'\n          <li><button type="button" class="thumb{on}" data-src="{b}" data-alt="{escape(alt)}" '
                   f'aria-label="Prikaži: {escape(POGLED.get(v, v))}" aria-pressed="{"true" if i == 0 else "false"}">'
                   f'<img src="{b}-800.webp" alt="" width="800" height="600" loading="lazy" decoding="async"></button></li>')
    specs = ''.join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in o['osobine'])
    clip = ''
    if o.get('par'):
        b, a = okvir_img_base(o, 'uporedjenje-bez'), okvir_img_base(o, 'uporedjenje-sa')
        clip = f'''
  <section class="section clip" aria-labelledby="clip-title">
    <div class="container clip-inner">
      <h2 class="h2" id="clip-title">Jedan okvir, dve namene</h2>
      <p class="lead center">Isti okvir nosite sa dioptrijom, a za sunce na njega zakačite clip-on staklo.</p>
      <div class="seg" role="group" aria-label="Prikaz okvira">
        <button type="button" class="seg-btn" data-clip="0" aria-pressed="false">Bez stakla</button>
        <button type="button" class="seg-btn is-on" data-clip="1" aria-pressed="true">Sa staklom</button>
      </div>
      <div class="clip-photo" id="clip-photo" data-on="1">
        {img(b, o['ime'] + ' bez sunčanog stakla', 1600, 1000, '(max-width: 760px) 100vw, 720px', 'clip-bez')}
        {img(a, o['ime'] + ' sa clip-on sunčanim staklom', 1600, 1000, '(max-width: 760px) 100vw, 720px', 'clip-sa')}
      </div>
    </div>
  </section>
'''
    if o.get('cena'):
        opts = ''.join(f'<option>{escape(x)}</option>' for x in STAKLA)
        buy = f'''<p class="model-price"><strong>{rsd(o["cena"])}</strong><span>Okvir sa clip-on sunčanim staklom. Cenu dioptrijskih stakala javljamo pre izrade.</span></p>
        <div class="buy" data-slug="{o["slug"]}" data-ime="{escape(o["ime"])}" data-cena="{o["cena"]}" data-slika="{okvir_img_base(o, (o.get("kartica") or ("uporedjenje-bez" if o.get("par") else "spreda")))}-800.webp">
          <label class="field"><span>Staklo</span><select class="buy-staklo">{opts}</select></label>
          <button type="button" class="btn btn-primary buy-add">Dodaj u korpu</button>
          <p class="buy-done" hidden>Dodato u korpu. <a class="text-link" href="/korpa/">Idi u korpu</a></p>
        </div>
        <p class="model-alt">Imate pitanje? <a class="text-link" href="{VIBER}">Pišite na Viber</a> ili pozovite <a class="text-link" href="tel:{TEL}">{TEL_TXT}</a>.</p>'''
    else:
        buy = f'''<p class="model-price"><strong>Cena na upit</strong><span>Pozovite ili pišite na Viber za cenu i dostupnost.</span></p>
        <div class="model-actions">
          <a href="{VIBER}" class="btn btn-primary">Pitajte za ovaj okvir</a>
          <a href="tel:{TEL}" class="btn btn-line">Pozovite {TEL_TXT}</a>
        </div>'''
    others = [x for x in OKVIRI if x['slug'] != o['slug']]
    same = [x for x in others if set(x['filteri']) & set(o['filteri'])]
    rest = [x for x in others if x not in same]
    related = (same + rest)[:4]
    rel = '\n'.join(kartica(x) for x in related)
    schema = [cs]
    if o.get('cena'):
        prod = {'@context': 'https://schema.org', '@type': 'Product', 'name': o['ime'], 'description': o['opis'],
                'image': [SITE + okvir_img_base(o, v) + '-1600.webp' for v in views],
                'offers': {'@type': 'Offer', 'price': str(o['cena']), 'priceCurrency': 'RSD',
                           'availability': 'https://schema.org/InStock', 'url': SITE + path}}
        if o.get('brend'):
            prod['brand'] = {'@type': 'Brand', 'name': o['brend']}
        schema.append(prod)
    sub = o.get('podnaslov', '')
    title_name = f'{o["ime"]}: {sub[:1].lower() + sub[1:]}' if sub else o['ime']
    html = head(f'{title_name} | Optika Visage',
                (o['opis'][:150].rsplit(' ', 1)[0] + '...') if len(o['opis']) > 155 else o['opis'],
                path, schema, og_image=okvir_img_base(o, views[0]) + '-1600.webp')
    html += nav('okviri') + '\n<main id="sadrzaj">\n'
    html += f'''
  <section class="page-head page-head--model">
    <div class="container">
      <nav aria-label="Putanja">{cr}</nav>
    </div>
  </section>

  <section class="model" aria-labelledby="model-title">
    <div class="container model-grid">
      <div class="gallery">
        <div class="gallery-main">{img(first, main_alt, 800, 600, '(max-width: 900px) 100vw, 55vw', 'gallery-img', lazy=False)}</div>
        <ul class="thumbs" aria-label="Fotografije okvira">{thumbs}
        </ul>
      </div>
      <div class="model-info">
        <p class="model-type">{escape(o.get("brend") or o["tip"].split(",")[0])}</p>
        <h1 class="model-title" id="model-title">{escape(o["ime"])}</h1>
        <p class="model-sub">{escape(o.get("podnaslov", o["tip"]))}</p>
        {buy}
        <p class="model-desc">{escape(o["opis"])}</p>
        <dl class="specs">{specs}</dl>
        <p class="model-note">Provera dioptrije je uračunata u cenu kompletnih naočara. <a class="text-link" href="/usluge/provera-dioptrije/">Kako izgleda provera</a></p>
      </div>
    </div>
  </section>
{clip}
  <section class="section wall" aria-labelledby="slicni-title">
    <div class="container">
      <h2 class="h2" id="slicni-title">Još okvira sa našeg zida</h2>
      <ul class="wall-grid">
{rel}
      </ul>
      <p class="center"><a href="/okviri/" class="btn btn-glass">Svi okviri</a></p>
    </div>
  </section>
'''
    html += '\n</main>\n' + FOOTER
    return write(path, html)


# ---------------------------------------------------------------- usluge

USLUGE = [
    {
        'slug': 'provera-dioptrije', 'naziv': 'Provera dioptrije', 'rok': '15 min',
        'title': 'Provera dioptrije na Voždovcu | Optika Visage, Medaković',
        'desc': 'Provera dioptrije u Optici Visage traje oko 15 minuta i uračunata je u cenu kompletnih naočara. TC Medaković 3, Voždovac.',
        'h1': 'Provera dioptrije na Voždovcu',
        'lead': 'Za oko 15 minuta, savremenom opremom i bez žurbe.',
        'kratko': 'Savremenom opremom, za oko 15 minuta. Uračunata u cenu kompletnih naočara.',
        'blokovi': [
            ('Koliko traje', 'Provera dioptrije traje oko 15 minuta. Obavlja je naš stručni tim savremenom opremom, bez žurbe i sa pravim savetom.'),
            ('Ko radi proveru', 'Optika Visage je optičarska radnja: proveru dioptrije radi naš stručni tim, ne lekar na licu mesta. Ako već imate recept spolja, rado ga prihvatamo i izrađujemo naočare tačno po njemu.'),
            ('Koliko košta', 'Proveru ne naplaćujemo posebno kada kod nas kupujete naočare: uračunata je u cenu kompletnih naočara, kada birate iz naše ponude ili kada ugrađujemo naša stakla u Vaš okvir. Ako ne kupujete naočare kod nas, javite nam se telefonom ili preko Vibera da proverimo uslove za Vaš slučaj.'),
            ('Da li treba zakazati', 'Zakazivanje nije obavezno, možete doći direktno u radnju. Ako želite da izbegnete čekanje, pozovite nas ili pišite na Viber pre dolaska.'),
            ('Posle provere', 'Birate okvir i stakla, a izrada naočara traje 1 do 5 dana. Vaša dioptrija se nakon izrade ispisuje na kesici uz naočare.'),
        ],
        'veze': ['izrada-po-receptu', 'stakla'],
    },
    {
        'slug': 'kontaktna-sociva', 'naziv': 'Kontaktna sočiva', 'rok': '',
        'title': 'Kontaktna sočiva na Voždovcu | Optika Visage, Medaković',
        'desc': 'Kontaktna sočiva Bausch+Lomb, Alcon, Leda i Cooper Vision u Optici Visage na Medakoviću, uz savet o pravom tipu sočiva.',
        'h1': 'Kontaktna sočiva na Voždovcu',
        'lead': 'Provereni brendovi i savet o tipu sočiva koji odgovara Vama.',
        'kratko': 'Bausch+Lomb, Alcon, Leda i Cooper Vision, uz savet o pravom tipu sočiva.',
        'blokovi': [
            ('Brendovi', 'Radimo sa proverenim brendovima: Bausch+Lomb, Alcon, Leda i Cooper Vision.'),
            ('Savet', 'Pomažemo Vam da izaberete tip sočiva koji odgovara Vašim potrebama i životnom stilu, uz savet o pravilnom korišćenju i nezi.'),
            ('Gde nas naći', 'Kontaktna sočiva možete kupiti kod nas, u Optici Visage u TC Medaković 3 na Voždovcu, srednji ulaz, lokal 45.'),
        ],
        'veze': ['provera-dioptrije', 'stakla'],
    },
    {
        'slug': 'stakla', 'naziv': 'Stakla za naočare', 'rok': '1 do 5 dana',
        'title': 'Stakla za naočare: antirefleks, progresivna, fotosenzitivna | Optika Visage',
        'desc': 'Antirefleks, stakla sa filterom za plavo svetlo, progresivna i fotosenzitivna stakla, i sunčana stakla u Vaš okvir. Optika Visage, Medaković.',
        'h1': 'Stakla za naočare',
        'lead': 'Izrađujemo sve vrste stakala, po proveri dioptrije ili po receptu.',
        'kratko': 'Antirefleks, plavo svetlo, progresivna i fotosenzitivna stakla, i sunčana stakla u Vaš okvir.',
        'blokovi': [
            ('Antirefleks', 'Sloj na staklu koji smanjuje odsjaj. Uz određene okvire antirefleks dobijate gratis.'),
            ('Filter za plavo svetlo', 'Stakla sa filterom za plavi deo svetla, na primer sa ekrana telefona i računara.'),
            ('Progresivna stakla', 'Jedno staklo za gledanje i na daljinu i na blizinu, sa postepenim prelazom jačine.'),
            ('Fotosenzitivna stakla', 'Stakla koja na suncu potamne, a u zatvorenom ponovo postanu svetla.'),
            ('Sunčana stakla u Vaš okvir', 'Ugrađujemo tonirana sunčana stakla u Vaš okvir, sa ili bez dioptrije. Jedan okvir tako postaje dve naočare za različite prilike.'),
            ('Clip-on', 'Dodatno sunčano staklo koje se kači na okvir sa dioptrijom. Imaju ga svi Tony Morgan okviri i Kubik.'),
        ],
        'veze': ['provera-dioptrije', 'izrada-po-receptu'],
    },
    {
        'slug': 'izrada-po-receptu', 'naziv': 'Izrada po receptu', 'rok': '1 do 5 dana',
        'title': 'Izrada naočara po receptu | Optika Visage, Voždovac',
        'desc': 'Izrada naočara po receptu bilo kog oftalmologa ili optometriste, za 1 do 5 dana. Optika Visage, TC Medaković 3.',
        'h1': 'Izrada naočara po receptu',
        'lead': 'Donesite recept, a mi izrađujemo naočare tačno po njemu.',
        'kratko': 'Recept od bilo kog oftalmologa. Sve vrste stakala, za 1 do 5 dana.',
        'blokovi': [
            ('Recept', 'Prihvatamo recepte od svih oftalmologa i optometrista i izrađujemo naočare po Vašoj specifikaciji.'),
            ('Stakla', 'Radimo sve vrste stakala: antirefleks, filter za plavo svetlo, progresivna i fotosenzitivna.'),
            ('Rok izrade', 'Izrada traje 1 do 5 dana, u zavisnosti od složenosti dioptrije i vrste stakala. Javljamo Vam se pozivom čim su naočare gotove.'),
        ],
        'veze': ['stakla', 'provera-dioptrije'],
    },
]
USL = {u['slug']: u for u in USLUGE}


def svc_rows(blocks):
    return '\n'.join(f'        <li><h3>{escape(t)}</h3><p>{escape(p)}</p></li>' for t, p in blocks)


def link_cards(slugs):
    out = ''
    for s in slugs:
        u = USL[s]
        out += (f'\n        <a class="link-card" href="/usluge/{s}/"><strong>{escape(u["naziv"])}</strong>'
                f'<span>{escape(u["kratko"])}</span></a>')
    return out


def build_usluge():
    cr, cs = breadcrumbs([('Početna', '/'), ('Usluge', '/usluge/')])
    rows = ''
    for u in USLUGE:
        t = f'<span class="svc-time">{u["rok"]}</span>' if u['rok'] else ''
        rows += f'\n        <li><h3><a href="/usluge/{u["slug"]}/">{escape(u["naziv"])}</a></h3>{t}<p>{escape(u["kratko"])}</p></li>'
    rows += ('\n        <li><h3><a href="/okviri/">Clip-on naočare</a></h3>'
             '<p>Dioptrijske naočare sa tamnim clip-on staklom za sunce.</p></li>')
    html = head('Usluge: provera dioptrije, sočiva, stakla | Optika Visage, Voždovac',
                'Provera dioptrije, dioptrijske naočare, izrada po receptu, kontaktna sočiva i sunčana stakla u Vaš okvir. Optika Visage, TC Medaković 3.',
                '/usluge/', [cs])
    html += nav('usluge') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Usluge', 'Provera dioptrije je uračunata u cenu kompletnih naočara.')
    html += f'''
  <section class="section services services--page" aria-label="Spisak usluga">
    <div class="container services-inner">
      <ul class="svc-list">{rows}
      </ul>
      <p class="svc-note">Antirefleks gratis uz određene okvire.<br>Plaćanje gotovinom, karticama, čekovima i na rate.</p>
    </div>
  </section>
'''
    html += cta_panel('Dođite na proveru', 'Zakazivanje nije obavezno. Ako ne želite da čekate, pozovite ili pišite na Viber.')
    html += '\n</main>\n' + FOOTER
    out = [write('/usluge/', html)]
    for u in USLUGE:
        path = f'/usluge/{u["slug"]}/'
        cr, cs = breadcrumbs([('Početna', '/'), ('Usluge', '/usluge/'), (u['naziv'], path)])
        html = head(u['title'], u['desc'], path, [cs])
        html += nav('usluge') + '\n<main id="sadrzaj">\n'
        html += page_head(cr, escape(u['h1']), escape(u['lead']))
        html += f'''
  <section class="section services services--page" aria-label="{escape(u["naziv"])}">
    <div class="container services-inner">
      <ul class="svc-list">
{svc_rows(u["blokovi"])}
      </ul>
    </div>
  </section>

  <section class="section related" aria-labelledby="vezano-title">
    <div class="container">
      <h2 class="h2" id="vezano-title">Povezane usluge</h2>
      <div class="link-cards">{link_cards(u["veze"])}
        <a class="link-card" href="/okviri/"><strong>Okviri</strong><span>Izbor okvira sa našeg zida, uključujući clip-on okvire.</span></a>
      </div>
    </div>
  </section>
'''
        html += cta_panel('Dođite u radnju', 'Zakazivanje nije obavezno. Ako ne želite da čekate, pozovite ili pišite na Viber.')
        html += '\n</main>\n' + FOOTER
        out.append(write(path, html))
    return out


# ---------------------------------------------------------------- o nama, kontakt, pitanja

FOTO_RADNJA = [
    ('radnja-visage-zid-i-pult', 'Zid sa Visage slovima i pult u radnji Optika Visage'),
    ('radnja-zid-sa-okvirima', 'Okviri na šipkama i posteri na zidu radnje'),
    ('radnja-zid-sa-okvirima-2', 'Zid sa okvirima i futrolama u radnji'),
    ('radnja-tester-suncanih-stakala', 'Tester sunčanih stakala u radnji'),
    ('radnja-decji-okvir-barbie', 'Roze Barbie dečji okvir uz roze Barbie futrolu'),
    ('radnja-posteri-oka', 'Posteri sa prikazom oka na zidu radnje'),
]

# Galerija radnje na /okviri/: cele fotografije (bez isecanja), širina i visina verzije od 800 px.
FOTO_GALERIJA = [
    ('radnja-visage-zid-i-pult', 'Zid sa Visage slovima i pult u radnji Optika Visage', 800, 600),
    ('radnja-zid-sa-okvirima', 'Okviri na šipkama i posteri na zidu radnje', 800, 1066),
    ('radnja-paneli-sa-okvirima', 'Dva panela sa okvirima i ogledalo između njih', 800, 1066),
    ('radnja-zid-sa-okvirima-2', 'Zid sa okvirima i futrolama u radnji', 800, 600),
    ('radnja-stalak-kod-izloga', 'Stalak sa naočarama kod izloga radnje', 800, 1066),
    ('radnja-tester-suncanih-stakala', 'Tester sunčanih stakala u radnji', 800, 1066),
    ('radnja-decji-okvir-barbie', 'Roze Barbie dečji okvir uz roze Barbie futrolu', 800, 1066),
    ('radnja-posteri-oka', 'Posteri sa prikazom oka na zidu radnje', 800, 1066),
]


def build_o_nama():
    cr, cs = breadcrumbs([('Početna', '/'), ('O nama', '/o-nama/')])
    photos = '\n'.join(f'        <figure class="photo">{img("/images/radnja/" + f, a, 800, 600, "(max-width: 760px) 100vw, 33vw")}</figure>'
                       for f, a in FOTO_RADNJA)
    html = head('O nama | Optika Visage, Medaković od 2021.',
                'Optika Visage na Medakoviću radi od 2021. Stručna provera dioptrije, savet bez žurbe i okviri za koje imate vremena da ih probate.',
                '/o-nama/', [cs])
    html += nav('o-nama') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Optika u kojoj se ne žuri', 'Optika Visage, Medaković, od 2021.')
    html += f'''
  <section class="section about" aria-label="O nama">
    <div class="container about-inner">
      <p class="about-lead">Otvorili smo radnju 2021. godine sa željom da svoje znanje i iskustvo pretvorimo u prostor u koji čovek ulazi i zna da će biti dočekan, ne samo sa osmehom, već i sa pravom informacijom o svojim očima i naočarama.</p>
      <p>Naš cilj je da svako pronađe svoj okvir. Onaj koji mu stoji, koji izdrži svakodnevicu i u kome se prepoznaje kada se pogleda u ogledalo. Ako za to treba sat vremena probanja, nema problema. Naočare se ne kupuju često, a pravi par menja kako se osećate.</p>
      <h2 class="h2 h2--small">Naš tim</h2>
      <p>Naš stručni tim brine o Vašim očima: od provere dioptrije i saveta o staklima i kontaktnim sočivima, preko izbora okvira i izrade naočara, do sitnih popravki i podešavanja. Posvećujemo Vam koliko god vremena treba da naočare budu baš onakve kakvim ih zamišljate.</p>
    </div>
  </section>

  <section class="section photos" aria-labelledby="radnja-foto-title">
    <div class="container">
      <h2 class="h2" id="radnja-foto-title">U našoj radnji</h2>
      <div class="photo-grid">
{photos}
      </div>{"" if PRODAVNICA else chr(10) + '      <p class="center photos-more"><a class="text-link" href="/okviri/#radnja">Još fotografija radnje</a></p>'}
    </div>
  </section>
'''
    html += cta_panel('Svratite na Medaković', 'Ponedeljak do petak 10 do 18 h, subota 9 do 14 h.')
    html += '\n</main>\n' + FOOTER
    return write('/o-nama/', html)


def build_kontakt():
    cr, cs = breadcrumbs([('Početna', '/'), ('Kontakt', '/kontakt/')])
    routes = ''.join(f'<li>{r}</li>' for r in ['29', '18', '18N', '20', '26L', '26Na', '29N', '312'])
    html = head('Kontakt i kako do nas | Optika Visage, TC Medaković 3',
                'Optika Visage, Braće Srnić 23a, TC Medaković 3, lokal 45, Beograd. Telefon i Viber 060 3175264. Radno vreme, prevoz i parking.',
                '/kontakt/', [cs])
    html += nav('kontakt') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Kontakt i kako do nas', 'Braće Srnić 23a, TC Medaković 3, srednji ulaz, lokal 45, 11050 Beograd')
    html += f'''
  <section class="section visit visit--page" aria-label="Kontakt podaci">
    <div class="container">
      <div class="visit-grid">
        <div class="visit-block">
          <h3>Radno vreme</h3>
          <table class="hours">
            <tbody>
              <tr><th scope="row">Ponedeljak do petak</th><td>10 do 18 h</td></tr>
              <tr><th scope="row">Subota</th><td>9 do 14 h</td></tr>
              <tr><th scope="row">Nedelja</th><td>zatvoreno</td></tr>
            </tbody>
          </table>
        </div>
        <div class="visit-block">
          <h3>Telefon i Viber</h3>
          <a href="tel:{TEL}" class="visit-phone">{TEL_TXT}</a>
          <div class="visit-actions">
            <a href="{VIBER}" class="btn btn-primary">Pišite na Viber</a>
            <a href="tel:{TEL}" class="btn btn-line">Pozovite</a>
            <a href="{MAPS_DIR}" class="btn btn-line visit-nav" target="_blank" rel="noopener">Navigacija do radnje</a>
          </div>
        </div>
        <div class="visit-block">
          <h3>Gradski prevoz do okretnice</h3>
          <ul class="routes" aria-label="Linije gradskog prevoza">{routes}</ul>
          <p>Okretnica Medaković 3, pa srednji ulaz u TC. Parking je ispred TC.</p>
        </div>
        <div class="visit-block">
          <h3>Email i mreže</h3>
          <ul class="contact-list">
            <li><a href="mailto:optikavisage@gmail.com">optikavisage@gmail.com</a></li>
            <li><a href="https://www.instagram.com/optika_visage/" rel="me noopener" target="_blank">Instagram @optika_visage</a></li>
            <li><a href="https://www.facebook.com/optikavisage" rel="me noopener" target="_blank">Facebook</a></li>
          </ul>
        </div>
        <div class="visit-block">
          <h3>Plaćanje</h3>
          <p>Gotovina, platne i kreditne kartice, čekovi i plaćanje na rate.</p>
        </div>
        <div class="visit-block">
          <h3>Firma</h3>
          <p>Optika Visage<br>PIB 112372621<br>MB 21660418</p>
        </div>
      </div>
      <div class="visit-map">
        <iframe src="https://maps.google.com/maps?q=Optika+Visage,+Bra%C4%87e+Srni%C4%87+23a,+Beograd&amp;t=&amp;z=17&amp;ie=UTF8&amp;iwloc=&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa: Optika Visage, TC Medaković 3"></iframe>
      </div>
      <p class="center visit-reviews"><a class="text-link" href="{MAPS_REVIEWS}" target="_blank" rel="noopener">Pročitajte naše Google recenzije</a></p>
    </div>
  </section>
'''
    html += '\n</main>\n' + FOOTER
    return write('/kontakt/', html)


def build_pitanja():
    cr, cs = breadcrumbs([('Početna', '/'), ('Pitanja', '/pitanja/')])
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage',
           'mainEntity': [{'@type': 'Question', 'name': q,
                           'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in PITANJA]}
    items = '\n'.join(f'        <details class="faq-item">\n          <summary>{escape(q)}</summary>\n          <p>{escape(a)}</p>\n        </details>'
                      for q, a in PITANJA)
    html = head('Česta pitanja | Optika Visage, Voždovac',
                'Odgovori na česta pitanja: provera dioptrije, rok izrade naočara, cene okvira, kontaktna sočiva, plaćanje, parking i radno vreme.',
                '/pitanja/', [cs, faq])
    html += nav('') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Česta pitanja', f'Niste našli odgovor? Pišite nam na Viber ili pozovite <a class="text-link" href="tel:{TEL}">{TEL_TXT}</a>.')
    html += f'''
  <section class="section faq" aria-label="Pitanja i odgovori">
    <div class="container faq-inner">
      <div class="faq-list">
{items}
      </div>
    </div>
  </section>
'''
    html += '\n</main>\n' + FOOTER
    return write('/pitanja/', html)


def build_korpa():
    if not PRODAVNICA:
        preusmeri('/korpa/', '/okviri/', 'Okviri')
        return
    cr, cs = breadcrumbs([('Početna', '/'), ('Korpa', '/korpa/')])
    opts = ''.join(f'<option>{escape(x)}</option>' for x in STAKLA)
    def eye(side, label):
        return (f'<div class="rx-row"><span class="rx-eye">{label}</span>'
                f'<label><span>SPH</span><input name="{side}_sph" inputmode="decimal" placeholder="npr. -1,25" autocomplete="off"></label>'
                f'<label><span>CYL</span><input name="{side}_cyl" inputmode="decimal" placeholder="npr. -0,50" autocomplete="off"></label>'
                f'<label><span>AX</span><input name="{side}_ax" inputmode="numeric" placeholder="0 do 180" autocomplete="off"></label></div>')
    html = head('Korpa | Optika Visage', 'Pregled izabranih okvira i slanje porudžbine Optici Visage.', '/korpa/', [cs])
    html = html.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    html += nav('') + '\n<main id="sadrzaj">\n'
    html += page_head(cr, 'Korpa', 'Pošaljite porudžbinu, a mi Vam se javljamo da potvrdimo stakla, cenu i termin dostave ili preuzimanja.')
    html += f'''
  <section class="section cart" aria-label="Korpa">
    <div class="container cart-inner">
      <div class="cart-empty" id="cart-empty" hidden>
        <p>Korpa je prazna.</p>
        <a href="/okviri/" class="btn btn-glass">Pogledaj naočare</a>
      </div>

      <form class="order" id="order" novalidate data-endpoint="https://formsubmit.co/ajax/{FORM_EMAIL}" hidden>
        <h2 class="order-h">Izabrani okviri</h2>
        <ul class="cart-list" id="cart-list"></ul>
        <template id="cart-item">
          <li class="cart-item">
            <img class="cart-img" alt="" width="800" height="500" loading="lazy">
            <div class="cart-body">
              <a class="cart-name"></a>
              <span class="cart-price"></span>
              <label class="field field--small"><span>Staklo</span><select class="cart-staklo">{opts}</select></label>
            </div>
            <button type="button" class="cart-remove" aria-label="Ukloni iz korpe">Ukloni</button>
          </li>
        </template>
        <p class="cart-total">Okviri ukupno: <strong id="cart-total">0 RSD</strong></p>
        <p class="cart-note">Cenu dioptrijskih stakala javljamo pre izrade. Provera dioptrije je uračunata u cenu kompletnih naočara.</p>

        <h2 class="order-h">Dioptrija</h2>
        <fieldset class="choice" id="rx-choice">
          <legend class="visually-hidden">Kako ćete nam dati dioptriju</legend>
          <label><input type="radio" name="dioptrija_nacin" value="Upisaću dioptriju" checked> Upisaću dioptriju</label>
          <label><input type="radio" name="dioptrija_nacin" value="Doneću recept u radnju"> Doneću recept u radnju</label>
          <label><input type="radio" name="dioptrija_nacin" value="Želim proveru dioptrije u radnji"> Želim proveru dioptrije u radnji</label>
        </fieldset>
        <div class="rx" id="rx">
          <p class="rx-help">Prepišite vrednosti sa recepta. SPH je jačina stakla, CYL i AX su vrednosti za astigmatizam, a PD je razmak između zenica. Polja koja nemate na receptu ostavite prazna.</p>
          {eye('od', 'Desno oko')}
          {eye('os', 'Levo oko')}
          <div class="rx-row rx-row--extra">
            <label><span>PD</span><input name="pd" inputmode="decimal" placeholder="npr. 62" autocomplete="off"></label>
            <label><span>ADD</span><input name="add" inputmode="decimal" placeholder="za progresivna" autocomplete="off"></label>
          </div>
        </div>

        <h2 class="order-h">Vaši podaci</h2>
        <div class="fields">
          <label class="field"><span>Ime i prezime *</span><input name="ime" required autocomplete="name"></label>
          <label class="field"><span>Telefon *</span><input name="telefon" required type="tel" inputmode="tel" autocomplete="tel"></label>
          <label class="field"><span>Email</span><input name="email" type="email" autocomplete="email"></label>
        </div>

        <h2 class="order-h">Dostava ili preuzimanje</h2>
        <fieldset class="choice" id="ship-choice">
          <legend class="visually-hidden">Kako želite da dobijete naočare</legend>
          <label><input type="radio" name="isporuka" value="Dostava na adresu" checked> Dostava na adresu u Beogradu</label>
          <label><input type="radio" name="isporuka" value="Preuzimanje u radnji"> Preuzimanje u radnji</label>
        </fieldset>
        <div class="ship" id="ship-adresa">
          <div class="fields">
            <label class="field"><span>Adresa *</span><input name="adresa" autocomplete="street-address" placeholder="ulica, broj, stan"></label>
            <label class="field"><span>Opština ili naselje *</span><input name="naselje" placeholder="npr. Voždovac"></label>
          </div>
          <p class="pickup"><strong>Besplatna dostava</strong> Naočare donosimo na Vašu adresu u Beogradu. Plaćanje pouzećem, gotovinom pri dostavi.</p>
        </div>
        <p class="pickup" id="ship-radnja" hidden><strong>Preuzimanje u radnji</strong> Braće Srnić 23a, TC Medaković 3, lokal 45. Plaćanje pri preuzimanju: gotovina, kartice, čekovi ili na rate.</p>
        <label class="field field--note"><span>Napomena</span><textarea name="napomena" rows="3"></textarea></label>
        <label class="consent"><input type="checkbox" name="saglasnost" required> Saglasan/na sam da Optika Visage koristi moje podatke, uključujući dioptriju, samo radi obrade ove porudžbine. *</label>
        <input type="text" name="_honey" class="visually-hidden" tabindex="-1" autocomplete="off" aria-hidden="true">
        <p class="order-error" id="order-error" role="alert" hidden></p>
        <button type="submit" class="btn btn-primary order-submit">Pošalji porudžbinu</button>
      </form>

      <div class="order-done" id="order-done" hidden>
        <h2 class="h2">Hvala, porudžbina je poslata.</h2>
        <p class="lead center">Javljamo Vam se telefonom da potvrdimo stakla, cenu i termin dostave ili preuzimanja.</p>
        <a href="/okviri/" class="btn btn-glass">Nazad na okvire</a>
      </div>
    </div>
  </section>
'''
    html += '\n</main>\n' + FOOTER
    write('/korpa/', html)


def build_pocetna_zid():
    """Upisuje kartice okvira na početnu, između oznaka ZID:START i ZID:END."""
    p = ROOT / 'index.html'
    s = p.read_text(encoding='utf-8')
    a, b = '<!-- ZID:START -->', '<!-- ZID:END -->'
    if a not in s:
        return
    izbor = ['kubik', 'tony-morgan-clip-on-1', 'tony-morgan-clip-on-2', 'tony-morgan-clip-on-3',
             'tony-morgan-clip-on-4', 'tony-morgan-clip-on-5', 'william-morris', 'diva-trend-roze-zlatni']
    po = {o['slug']: o for o in OKVIRI}
    cards = '\n'.join(kartica(po[x]) for x in izbor if x in po)
    i, j = s.index(a) + len(a), s.index(b)
    p.write_text(s[:i] + '\n' + cards + '\n      ' + s[j:], encoding='utf-8')


def build_sitemap(paths):
    urls = ['/'] + paths
    body = ''.join(f'  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>\n' for p in urls)
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + '</urlset>\n', encoding='utf-8')


def main():
    paths = [build_katalog()]
    paths += [p for p in (build_model(o) for o in OKVIRI) if p]
    paths += build_usluge()
    paths += [build_o_nama(), build_kontakt(), build_pitanja()]
    build_korpa()
    build_pocetna_zid()
    build_sitemap(paths)
    print(len(paths), 'stranica:', ' '.join(paths))


if __name__ == '__main__':
    main()
