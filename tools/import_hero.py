"""Prepares the hero phones and the store badges from the originals in src/originals/ (transparent WebP):
phone_home / phone_profile / phone_article.webp -> src/hero/, store_badges.webp (App Store + Google Play side by side)
-> src/badges/app-store.webp and google-play.webp.
    python tools/import_hero.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / 'src/originals'
HERO = ROOT / 'src/hero'
BADGES = ROOT / 'src/badges'
PHONE_W = 560
BADGE_H = 144


def opaque_box(im):
    return im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()


def main():
    HERO.mkdir(parents=True, exist_ok=True)
    BADGES.mkdir(parents=True, exist_ok=True)
    for name in ('phone_home', 'phone_profile', 'phone_article'):
        im = Image.open(ORIG / f'{name}.webp').convert('RGBA')
        im = im.crop(opaque_box(im))
        im = im.resize((PHONE_W, round(im.height * PHONE_W / im.width)), Image.LANCZOS)
        im.save(HERO / f'{name}.webp', 'WEBP', quality=86, method=6)
        print(name, im.size)

    im = Image.open(ORIG / 'store_badges.webp').convert('RGBA')
    alpha = im.getchannel('A').point(lambda v: 255 if v > 8 else 0)
    cols = [alpha.crop((x, 0, x + 1, im.height)).getbbox() is not None for x in range(im.width)]
    runs, start = [], None
    for x, filled in enumerate(cols + [False]):
        if filled and start is None:
            start = x
        elif not filled and start is not None:
            runs.append((start, x))
            start = None
    assert len(runs) == 2, runs
    for (x0, x1), name in zip(runs, ('app-store', 'google-play')):
        part = im.crop((x0, 0, x1, im.height))
        part = part.crop(opaque_box(part))
        part = part.resize((round(part.width * BADGE_H / part.height), BADGE_H), Image.LANCZOS)
        part.save(BADGES / f'{name}.webp', 'WEBP', lossless=True, method=6)
        print(name, part.size)


if __name__ == '__main__':
    main()
