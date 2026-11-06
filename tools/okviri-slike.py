"""
Obrada fotografija okvira za sajt.

Ulaz: folder sa podfolderima 1..14 i Futrola, kao u "Visage Slike za sajt" (JPG, do 2400 px).
Izlaz: images/okviri/<model>/<model>-<pogled>-800.webp i -1600.webp
       za clip-on modele poravnat par images/okviri/<model>/<model>-uporedjenje-{bez,sa}-{800,1600}.webp
       a za ostale izrez 8:5 oko okvira images/okviri/<model>/<model>-kartica-{800,1600}.webp

Pozadina svake fotografije se posvetli na istu svetlo sivu (#ECECEE), da svi okviri
stoje na istoj podlozi kao na sajtu. Nazivi modela prate NAZIVI_OKVIRA.md.

Upotreba (iz korena repoa):
    python3 tools/okviri-slike.py "putanja/do/Visage Slike za sajt"
Potrebno: pip install numpy pillow
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TARGET = np.array([236., 236., 238.])

# model -> folder, {pogled: broj fajla}, (bez, sa) za poravnat par ili None
MODELI = {
    'kubik': ('1', {'spreda': '100', 'poluprofil': '103', 'profil': '105',
                    'clip-on-spreda': '109', 'clip-on-poluprofil': '110'}, ('100', '109')),
    'tony-morgan-sampanj': ('2', {'spreda': '96', 'poluprofil': '94', 'profil': '92', 'clip-on-spreda': '88',
                                  'clip-on-poluprofil': '90', 'clip-on-profil': '91', 'futrola': '70'}, ('96', '88')),
    'tony-morgan-leptir': ('7', {'spreda': '39', 'poluprofil': '40', 'profil': '41', 'clip-on-spreda': '44',
                                 'clip-on-poluprofil': '45', 'clip-on-profil': '43', 'futrola': '77'}, ('39', '44')),
    'tony-morgan-cat-eye': ('8', {'spreda': '33', 'poluprofil': '34', 'profil': '32', 'clip-on-spreda': '27',
                                  'clip-on-poluprofil': '28', 'clip-on-profil': '31', 'futrola': '75',
                                  'futrola-otvorena-1': '15', 'futrola-otvorena-2': '17', 'futrola-otvorena-3': '19',
                                  'futrola-otvorena-4': '21', 'clip-on-pored': '38'}, ('33', '27')),
    'tony-morgan-okrugli': ('9', {'spreda': '47', 'poluprofil': '49', 'profil': '51', 'clip-on-spreda': '53',
                                  'clip-on-poluprofil': '54', 'clip-on-profil': '52', 'futrola': '73'}, ('47', '53')),
    'tony-morgan-pravougaoni': ('10', {'spreda': '57', 'spreda-2': '58', 'poluprofil': '60', 'profil': '62',
                                       'clip-on-spreda': '66', 'clip-on-poluprofil': '68', 'clip-on-profil': '64',
                                       'futrola': '71'}, ('58', '66')),
    'crni-cat-eye-acetat': ('11', {'clip-on-podignut': '1', 'poluprofil': '3', 'otpozadi': '5', 'sa-strane': '6',
                                   'spreda': '8'}, None),
    'diva-trend-zlatni': ('12', {'profil': '1000027511', 'spreda': '1000027512'}, None),
    'william-morris': ('13', {'spreda': '1000027507', 'profil': '1000027508', 'spreda-2': '1000027509'}, None),
    'diva-trend-roze-zlatni': ('14', {'spreda': '1000027503', 'profil': '1000027504', 'sklopljen': '1000027505'}, None),
    'tony-morgan-crni-sportski': ('3', {'futrola': '86'}, None),
    'tony-morgan-plave-drske': ('4', {'futrola': '84'}, None),
    'tony-morgan-crni-pravougaoni': ('5', {'futrola': '82'}, None),
    'futrola-tony-morgan': ('Futrola', {'otvorena-1': '10', 'otvorena-2': '11', 'otvorena-3': '13',
                                        'zatvorena-1': '23', 'zatvorena-2': '69'}, None),
}
# crni sjajni cat-eye na futroli (folder 6) je po izgledu isti model kao folder 11
DODATNO = {'crni-cat-eye-acetat': ('6', {'futrola': '79'})}

# Kartica po prednjem delu okvira (x0, y0, x1, y1 na fotografiji spreda od 2400 px), za modele
# kod kojih automatski izrez ne uspeva (tanki metalni okviri, okvir skoro preko cele fotografije).
# Kartica tada stoji isto kao poravnati parovi clip-on okvira: okvir zauzima 79% širine,
# a donja ivica okvira je na 75,5% visine, pa svi okviri na zidu stoje na istoj liniji.
KARTICA_PREDNJI = {
    'william-morris': (120, 504, 2250, 1305),
    'diva-trend-roze-zlatni': (114, 375, 2295, 1146),
    'diva-trend-zlatni': (246, 735, 2040, 1320),
}
PREDNJI_SIRINA, PREDNJI_DNO = .79, .755
PORAVNAT_DNO = .70  # velika fotografija 4:3 u galeriji: donja ivica okvira na 70% visine


def lift(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float64)
    h = a.shape[0]
    med = np.median(a[:max(8, int(h * .08))].reshape(-1, 3), axis=0)
    return Image.fromarray(np.clip(a * (TARGET / med), 0, 255).astype(np.uint8))


def save(im, out_base):
    for w in (800, 1600):
        im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(f'{out_base}-{w}.webp', quality=82, method=6)


def frame_box(im):
    g = np.asarray(im.convert('L'), dtype=np.float64)
    m = g < 150
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def _silhouette(im, w):
    """Ispunjen obris okvira (sve što nije pozadina, sa ispunjenim staklima), umanjen na širinu w."""
    g = im.convert('RGB').resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    a = np.asarray(g, dtype=np.float64)
    m = (np.abs(a - TARGET).sum(axis=2) > 75).astype(np.uint8) * 255
    mi = Image.fromarray(m).filter(ImageFilter.MaxFilter(3))
    # sve što je spojeno sa ivicom slike je spoljašnjost; ostalo (i unutrašnjost stakala) je obris
    for xy in [(0, 0), (mi.width - 1, 0), (0, mi.height - 1), (mi.width - 1, mi.height - 1)]:
        if mi.getpixel(xy) == 0:
            ImageDraw.floodfill(mi, xy, 128)
    return (np.asarray(mi) != 128).astype(np.float64)


def _best_shift(ma, mb):
    H, W = max(ma.shape[0], mb.shape[0]), max(ma.shape[1], mb.shape[1])
    A = np.zeros((H, W)); B = np.zeros((H, W))
    A[:ma.shape[0], :ma.shape[1]] = ma; B[:mb.shape[0], :mb.shape[1]] = mb
    c = np.fft.irfft2(np.fft.rfft2(A) * np.conj(np.fft.rfft2(B)), s=(H, W))
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    inter = c[iy, ix]
    if iy > H // 2: iy -= H
    if ix > W // 2: ix -= W
    iou = inter / (A.sum() + B.sum() - inter + 1e-9)
    return ix, iy, iou


def align_pair(a, b):
    """Poravna b na a po obrisu okvira: proba razmere 0.85 do 1.15, uzima najveće preklapanje."""
    W = 480
    ma = _silhouette(a, W)
    best = None
    for s in np.arange(.85, 1.1501, .01):
        mb = _silhouette(b, round(W * s * b.width / a.width))
        dx, dy, iou = _best_shift(ma, mb)
        if best is None or iou > best[0]:
            best = (iou, s, dx, dy)
    iou, s, dx, dy = best
    if abs(s - 1) > .004:
        b = b.resize((round(b.width * s), round(b.height * s)), Image.LANCZOS)
    k = a.width / W
    ox, oy = dx * k, dy * k
    box = frame_box_85(a)
    fill = tuple(int(v) for v in TARGET)
    ca = safe_crop(a, box)
    cb = safe_crop(b, (round(box[0] - ox), round(box[1] - oy), round(box[2] - ox), round(box[3] - oy)))
    return ca, cb, s, (ox, oy, iou)


def frame_box_85(a):
    """Izrez 8:5 oko okvira na fotografiji."""
    ys, xs = np.nonzero(_silhouette(a, a.width // 4))
    x0, x1 = np.percentile(xs, [1, 99]) * 4; y0, y1 = np.percentile(ys, [1, 99]) * 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cw = min(a.width * .96, (x1 - x0) * 1.36)
    ch = cw * 5 / 8
    return (round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))


def _pad_bg(a, left, right, top, bottom, band=80, smooth=41):
    """Produži pozadinu: svaki novi red/kolona dobija boju pozadine iz trake uz ivicu.
    U obzir ulaze samo svetli, sivi pikseli trake, pa se okvir i drške ne razvlače u pruge."""
    k = np.ones(smooth) / smooth
    def side(edge):  # edge: (H, band, 3) -> (H, 3) izglađena boja pozadine po redovima
        sat = edge.max(axis=2) - edge.min(axis=2)
        ok = (sat < 22) & (edge.mean(axis=2) > 185)
        m = np.full((edge.shape[0], 3), np.nan)
        for y in range(edge.shape[0]):
            px = edge[y][ok[y]]
            if len(px) >= 10:
                m[y] = np.median(px, axis=0)
        i = np.arange(len(m)); good = ~np.isnan(m[:, 0])
        m = np.stack([np.interp(i, i[good], m[good, c]) for c in range(3)], axis=1)
        return np.stack([np.convolve(np.pad(m[:, c], smooth // 2, mode='edge'), k, 'valid') for c in range(3)], axis=1)
    if left:
        a = np.concatenate([np.repeat(side(a[:, :band])[:, None], left, axis=1), a], axis=1)
    if right:
        a = np.concatenate([a, np.repeat(side(a[:, -band:])[:, None], right, axis=1)], axis=1)
    if top:
        a = np.concatenate([np.repeat(side(a[:band].transpose(1, 0, 2))[None], top, axis=0), a], axis=0)
    if bottom:
        a = np.concatenate([a, np.repeat(side(a[-band:].transpose(1, 0, 2))[None], bottom, axis=0)], axis=0)
    return a


def kartica_po_prednjem(im, front, aspect=8 / 5, dno=PREDNJI_DNO):
    """Izrez u kome prednji deo okvira stoji kao na poravnatim parovima (vidi KARTICA_PREDNJI).
    aspect 8/5 je kartica za zid, 4/3 je velika fotografija u galeriji (ista širina okvira, više pozadine)."""
    x0, y0, x1, y1 = front
    w = (x1 - x0) / PREDNJI_SIRINA
    h = w / aspect
    cx = (x0 + x1) / 2
    bx = [round(cx - w / 2), round(y1 - dno * h)]
    bx += [bx[0] + round(w), bx[1] + round(h)]
    a = np.asarray(im.convert('RGB'), dtype=np.float64)
    pl, pt = max(0, -bx[0]), max(0, -bx[1])
    pr, pb = max(0, bx[2] - im.width), max(0, bx[3] - im.height)
    a = _pad_bg(a, pl, pr, pt, pb)
    a = a[bx[1] + pt:bx[3] + pt, bx[0] + pl:bx[2] + pl]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def prednji_iz_para(im):
    """Prednji deo okvira na fotografiji spreda, procenjen iz izreza 8:5 kao kod poravnatih parova."""
    x0, y0, x1, y1 = frame_box_85(im)
    w, h = x1 - x0, y1 - y0
    m = (1 - PREDNJI_SIRINA) / 2
    return (x0 + m * w, y0 + .3 * h, x1 - m * w, y0 + PREDNJI_DNO * h)


def safe_crop(im, bx):
    canvas = Image.new('RGB', (bx[2] - bx[0], bx[3] - bx[1]), tuple(int(v) for v in TARGET))
    canvas.paste(im, (-bx[0], -bx[1]))
    return canvas


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out_root = Path(__file__).resolve().parent.parent / 'images' / 'okviri'
    for model, (folder, views, pair) in MODELI.items():
        od = out_root / model
        od.mkdir(parents=True, exist_ok=True)
        cache = {}
        allviews = dict(views)
        jobs = [(folder, v, n) for v, n in views.items()]
        if model in DODATNO:
            f2, v2 = DODATNO[model]
            jobs += [(f2, v, n) for v, n in v2.items()]
        for f, v, n in jobs:
            p = src / f / f'{n}.jpg'
            im = lift(Image.open(p))
            cache[n] = im
            save(im, od / f'{model}-{v}')
        if not pair and 'spreda' in views:
            im = cache[views['spreda']]
            if model in KARTICA_PREDNJI:
                save(kartica_po_prednjem(im, KARTICA_PREDNJI[model]), od / f'{model}-kartica')
                save(kartica_po_prednjem(im, KARTICA_PREDNJI[model], 4 / 3, PORAVNAT_DNO), od / f'{model}-poravnat')
            else:
                save(safe_crop(im, frame_box_85(im)), od / f'{model}-kartica')
        if pair:
            ca, cb, s, off = align_pair(cache[pair[0]], cache[pair[1]])
            save(ca, od / f'{model}-uporedjenje-bez')
            save(cb, od / f'{model}-uporedjenje-sa')
            a = cache[pair[0]]
            save(kartica_po_prednjem(a, prednji_iz_para(a), 4 / 3, PORAVNAT_DNO), od / f'{model}-poravnat')
            print(model, 'par: razmera %.2f, pomeraj %.0f,%.0f, preklapanje %.2f' % (s, *off))
        print(model, len(jobs), 'slika')


if __name__ == '__main__':
    main()
