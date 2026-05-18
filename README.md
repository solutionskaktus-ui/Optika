# Optika Visage — Sajt

Statički sajt za **Optika Visage**, Medaković 3, Beograd.
Premium minimalistički dizajn, optimizovan za SEO i lokalne pretrage.

🌐 **Live:** [visageoptika.rs](https://visageoptika.rs/) *(nakon postavljanja domena)*

---

## 📁 Struktura projekta

```
visage-site/
├── index.html              ← Glavna stranica (single-page)
├── 404.html                ← Stranica za nepostojeće URL-ove
├── sitemap.xml             ← Mapa sajta za Google
├── robots.txt              ← Pravila za pretraživače
├── CNAME                   ← Custom domain za GitHub Pages
├── .nojekyll               ← Isključuje Jekyll obradu
├── visage-optika-logo-full.svg  ← Vektorski logo
├── css/
│   └── styles.css          ← Stilovi
├── js/
│   └── main.js             ← JavaScript (mobile menu, scroll reveal)
├── images/                 ← JPG slike (fallback)
├── images-webp/            ← WebP slike (primarno)
└── favicons/               ← Set favikona za sve uređaje
```

---

## 🚀 Postavljanje na GitHub Pages

### Korak 1 — Kreiraj repository

1. Na GitHubu napravi novi repo, npr. `visage-site` ili `visageoptika.rs`
2. **Public** mora biti (za besplatne GitHub Pages)

### Korak 2 — Upload fajlove

Sve fajlove iz ove arhive ubaci u root repository-ja.

Preko terminala:
```bash
git init
git add .
git commit -m "Initial commit — Optika Visage site"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### Korak 3 — Uključi GitHub Pages

1. Idi na **Settings → Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `main` / `(root)`
4. Sačekaj 1–2 minuta dok se sajt ne deploy-uje

Sajt će biti dostupan na: `https://USERNAME.github.io/REPO/`

### Korak 4 — Postavi custom domain

1. Kupi domen (preporuka: `visageoptika.rs` na RNIDS ili kod registara kao GoDaddy, Loopia)
2. U DNS panelu domena dodaj A zapise koji pokazuju na GitHub Pages IP adrese:
   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`

   Ili CNAME za `www`: pokazuje na `USERNAME.github.io`
3. U **Settings → Pages → Custom domain** unesi `visageoptika.rs`
4. Označi **Enforce HTTPS** kada bude dostupno (par sati nakon povezivanja)

---

## ✏️ Šta ažurirati pre objavljivanja

### 1. Adresa stvarne domene (sve linije sa `visageoptika.rs`)
Ako koristiš drugu domenu, zameni u:
- `index.html` (canonical, OG tags, schema)
- `sitemap.xml` (svi URL-ovi)
- `robots.txt` (sitemap URL)
- `CNAME` (samo domen)

### 2. Google Analytics i Search Console
Pre stavljanja u produkciju:
1. Postavi **Google Analytics 4** (GA4) — generiše tracking kod
2. Ubaci taj kod u `<head>` u `index.html`
3. Verifikuj sajt u **Google Search Console** (visageoptika.rs)
4. Submituj `sitemap.xml` kroz Search Console

### 3. Place ID za Google mapu
Trenutno embed-ovan placeholder URL za mapu. Posle live-a:
1. Idi na Google Maps → Optika Visage
2. Klikni "Share" → "Embed a map"
3. Kopiraj `<iframe>` kod
4. Zameni u `index.html` u `.contact-map` sekciji

### 4. Recenzije
Trenutno 3 generičke recenzije. Posle prvih 10+ pravih Google recenzija:
1. Kopiraj 3 najjače
2. Zameni u `index.html` u sekciji `.reviews-grid`
3. Dodaj puno ime klijenta (ako su saglasni)

---

## 🎨 Brand sistem

```css
--primary: #5B0070   /* Ljubičasta — primary */
--accent:  #FFDA72   /* Žuta — accent */
--ink:     #0E0E0E   /* Tekst */
--bg:      #FFFFFF   /* Pozadina */
```

**Tipografija:**
- Display: `Fraunces` (Google Fonts) — serif sa karakterom za naslove
- Body: `Rethink Sans` (Google Fonts) — isti font kao u logotipu

---

## 📊 SEO — Implementirano

✅ Schema.org Optician markup (LocalBusiness varijanta)
✅ FAQPage schema (za rich snippet u Google)
✅ Open Graph meta tagovi (za WhatsApp, Facebook, IG share)
✅ Twitter Card meta tagovi
✅ Canonical URL
✅ XML sitemap
✅ robots.txt
✅ Alt textovi na svim slikama (SEO + a11y)
✅ Semantic HTML5 (header, nav, section, article, footer)
✅ Mobile-first responsive design
✅ WebP slike sa JPG fallback
✅ Preconnect za Google Fonts (brži render)
✅ Lazy loading za slike ispod fold-a

## 🔧 Performanse

- WebP slike: ~10–35KB svaka (originalno 1–2.5MB)
- CSS: jedan fajl, ispod 25KB
- JS: minimal, ispod 4KB
- Bez heavy framework-a — vanilla HTML/CSS/JS
- Ciljani Lighthouse score: **95+ / 100**

---

## 🛠️ Razvoj lokalno

Sajt je statički — možeš ga otvoriti direktno u browseru, ali bolje je da pokrećeš lokalni server (zbog CORS i path-ova):

```bash
# Python 3
python3 -m http.server 8000

# Node (npx)
npx serve

# PHP
php -S localhost:8000
```

Otvori `http://localhost:8000` u browseru.

---

## 📝 Naredne preporuke

1. **Fotografija Ružice** za About sekciju (zameni placeholder)
2. **Fotografija enterijera radnje** + izlog spolja
3. **Clip-on dedicated landing page** (`/clip-on/`) — SEO niša bez konkurencije
4. **Blog sekciju** sa savetima (1 post mesečno) — za organic SEO rast
5. **Instagram feed embed** kada budu krenuli sa redovnim postovima

---

## 📞 Kontakt vlasnika

- **Optika Visage**
- Braće Srnić 23a, lokal 45, TC Medaković 3, Beograd
- Tel: 060 3175264 · 064 1255052
- Email: optikavisage@gmail.com

---

© 2026 Optika Visage. Sva prava zadržana.
