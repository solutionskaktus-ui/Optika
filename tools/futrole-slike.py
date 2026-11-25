"""Pravi fotografije futrola za sajt iz originalnih fotografija (bela pozadina).

Pokretanje:  python tools/futrole-slike.py <folder sa originalnim JPG fotografijama>

Spisak futrola i fotografija je u data/futrole.json. Svaka fotografija se iseče oko
futrole i stavi na belu podlogu 4:3, tako da futrola zauzima isti deo kadra:
najviše 82 % širine i 64 % visine, na sredini. Izlaz:
images/futrole/<model>/<model>-<boja>-<redni broj>-800.webp, -1600.webp i sličica -240.webp
"""
import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
W, H = 1600, 1200
MAX_W, MAX_H = .82, .64


def slug(s):
    s = s.lower().replace('đ', 'dj')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return '-'.join(''.join(c if c.isalnum() else ' ' for c in s).split())


def okvir_predmeta(a, prag=248):
    """Granice futrole (sa senkom): redovi i kolone gde ima bar nekoliko ne-belih piksela."""
    m = a.min(2) < prag
    rows, cols = np.where(m.sum(1) > 3)[0], np.where(m.sum(0) > 3)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


def obradi(src, out_base):
    im = Image.open(src)
    im.draft('RGB', (2400, 1600))
    im = ImageOps.exif_transpose(im).convert('RGB')
    x0, y0, x1, y1 = okvir_predmeta(np.asarray(im))
    pad = int(.01 * im.width)
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    obj = im.crop((x0, y0, x1, y1))
    s = min(MAX_W * W / obj.width, MAX_H * H / obj.height)
    obj = obj.resize((round(obj.width * s), round(obj.height * s)), Image.LANCZOS)
    can = Image.new('RGB', (W, H), 'white')
    can.paste(obj, ((W - obj.width) // 2, (H - obj.height) // 2))
    out_base.parent.mkdir(parents=True, exist_ok=True)
    can.save(f'{out_base}-1600.webp', quality=80, method=6)
    can.resize((800, 600), Image.LANCZOS).save(f'{out_base}-800.webp', quality=80, method=6)
    slicica(out_base)


def slicica(out_base):
    Image.open(f'{out_base}-800.webp').convert('RGB').resize((240, 180), Image.LANCZOS).save(f'{out_base}-240.webp', quality=78, method=6)


def main():
    src_dir = Path(sys.argv[1])
    data = json.loads((ROOT / 'data' / 'futrole.json').read_text(encoding='utf-8'))
    n = 0
    for m in data['modeli']:
        for f in m['futrole']:
            for i, (foto, _pogled) in enumerate(f['foto'], 1):
                base = ROOT / 'images' / 'futrole' / m['slug'] / f'{m["slug"]}-{slug(f["boja"])}-{i}'
                if Path(f'{base}-800.webp').exists() and '--sve' not in sys.argv:
                    if not Path(f'{base}-240.webp').exists():
                        slicica(base)
                    continue
                obradi(src_dir / f'{foto}.jpg', base)
                n += 1
                print(base.relative_to(ROOT))
    print(n, 'fotografija')


if __name__ == '__main__':
    main()
