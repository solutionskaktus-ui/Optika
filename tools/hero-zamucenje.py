"""
Pravi pozadine za hero sekciju: istu fotografiju u 21 nivou zamućenja,
od 0,00 do -5,00 dioptrije u koracima od 0,25 (21 nivo).

Zamućenje simulira kratkovidost: konvolucija diskom (ne Gausovo zamućenje),
u linearnom svetlu. Prečnik kruga zamućenja (rad) ~ prečnik zenice (m) x defokus (D).
Pretpostavka: zenica 4 mm. Telefon na ~30 cm daje ~7.7 CSS px prečnika po dioptriji,
desktop na ~60 cm ~8.7 CSS px po dioptriji. Ovo je model, ne merenje.

Upotreba (iz korena repoa):
    python3 tools/hero-zamucenje.py putanja/do/fotografije.jpg

Rezultat: images/hero/hero-p-00.webp ... hero-p-20.webp (telefon, uspravno 780x1688)
          images/hero/hero-d-00.webp ... hero-d-20.webp (desktop, položeno 1920x1200)
Broj u imenu je korak: 00 = 0,00 D (oštro), 20 = -5,00 D.
Potrebno: pip install numpy pillow
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

STEPS = 20  # 20 koraka po 0,25 = -5,00 D; mora da se slaže sa STEPS u js/main.js


def srgb_to_linear(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055) * 255


def disc_blur(img, radius):
    if radius < 0.5:
        return img.copy()
    arr = srgb_to_linear(np.asarray(img.convert('RGB'), dtype=np.float64))
    r = int(np.ceil(radius)) + 1
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    kernel = np.clip(radius + 0.5 - np.sqrt(x * x + y * y), 0, 1)
    kernel /= kernel.sum()
    pad = np.pad(arr, ((r, r), (r, r), (0, 0)), mode='reflect')
    h, w = pad.shape[:2]
    k = np.zeros((h, w))
    k[:2 * r + 1, :2 * r + 1] = kernel
    fk = np.fft.rfft2(np.roll(k, (-r, -r), axis=(0, 1)))
    out = np.stack([np.fft.irfft2(np.fft.rfft2(pad[..., c]) * fk, s=(h, w)) for c in range(3)], -1)
    return Image.fromarray(linear_to_srgb(out[r:-r, r:-r]).astype(np.uint8))


def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    left, top = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((left, top, left + w, top + h))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Image.open(sys.argv[1]).convert('RGB')
    out = Path(__file__).resolve().parent.parent / 'images' / 'hero'
    out.mkdir(parents=True, exist_ok=True)
    # (oznaka, širina, visina, image px prečnika po dioptriji)
    sets = [('p', 780, 1688, 15.4),   # telefon @2x: 7.7 CSS px/D
            ('d', 1920, 1200, 11.6)]  # desktop: 8.7 CSS px/D pri prikazu na ~1440 px
    for tag, w, h, per_d in sets:
        base = cover(src, w, h)
        for step in range(STEPS + 1):
            d = step * 0.25
            disc_blur(base, per_d * d / 2).save(out / f'hero-{tag}-{step:02d}.webp', quality=80, method=6)
        print(tag, 'gotovo')


if __name__ == '__main__':
    main()
