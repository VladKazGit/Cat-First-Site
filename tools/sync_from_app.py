"""Copies what the site needs from the Android app repo (read-only there) into app_data/ and src/img/.

Run after the app's content or strings change, then run build.py:
    python tools/sync_from_app.py
    python tools/build.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
APP = Path('C:/Users/mango/AndroidStudioProjects/Cat_First-Android/app/src/main')
IOS_TEXTS = Path('C:/Users/mango/AppData/Local/Temp/cfios/ios/APP_STORE_TEXTS.md')
DATA = ROOT / 'app_data'
IMG = ROOT / 'src/img'
ICONS = ROOT / 'src/icons'

# site language -> (content file suffix, values dir)
LANGS = {
    'ru': ('ru', 'values-ru'), 'en': ('en', 'values'), 'uk': ('uk', 'values-uk'), 'de': ('de', 'values-de'),
    'es': ('es', 'values-es'), 'fr': ('fr', 'values-fr'), 'it': ('it', 'values-it'), 'pl': ('pl', 'values-pl'),
    'pt-br': ('pt', 'values-pt-rBR'), 'tr': ('tr', 'values-tr'), 'kk': ('kk', 'values-kk'), 'el': ('el', 'values-el'),
    'sr': ('sr', 'values-sr'), 'bs': ('bs', 'values-bs'),
}
CONTENT = ['safe_home_categories', 'home_articles', 'knowledge', 'checklists', 'emergency']
STRING_KEYS = ['nav_home_safety', 'nav_knowledge', 'nav_checklists', 'nav_emergency', 'knowledge_hub_title',
               'knowledge_hub_intro', 'safe_home_intro', 'checklists_title', 'emergency_banner_title',
               'emergency_banner_body', 'emergency_critical_situations', 'emergency_urgent_today_title',
               'emergency_critical_badge', 'about_section_title', 'settings_support_section_title', 'disclaimer_text',
               'generic_expand', 'generic_collapse', 'home_settings_link',
               'nav_my_cat']  # not shown on the site: check.py makes sure it never appears
MAX_W = 1200
SMALL_WIDTHS = (480, 800)  # extra copies for srcset: phones and small slots take these instead of the full one


def android_unescape(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] == '"':
        s = s[1:-1]
    return (s.replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('&lt;', '<').replace('&gt;', '>')
            .replace('&amp;', '&'))


def app_strings(values_dir):
    xml = (APP / 'res' / values_dir / 'strings.xml').read_text(encoding='utf-8')
    out = {}
    for k in STRING_KEYS:
        m = re.search(rf'<string name="{k}"[^>]*>(.*?)</string>', xml, re.S)
        out[k] = android_unescape(m.group(1)) if m else None
    m = re.search(r'<string-array name="emergency_urgent_reasons">(.*?)</string-array>', xml, re.S)
    out['emergency_urgent_reasons'] = [android_unescape(i) for i in re.findall(r'<item>(.*?)</item>', m.group(1), re.S)]
    return out


def ios_disclaimers():
    """Disclaimer per content suffix from APP_STORE_TEXTS.md, section 'Disclaimer'."""
    text = IOS_TEXTS.read_text(encoding='utf-8').split('## Disclaimer', 1)[1]
    text = re.split(r'\n## ', text)[0]
    out = {}
    for m in re.finditer(r'### .*?\(`([a-z]+)`\)\s*\n\s*\n(.+?)(?=\n\s*\n|\Z)', text, re.S):
        out[m.group(1)] = m.group(2).strip()
    return out


def image_names():
    names = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('image', 'heroImage') and v:
                    names.add(v)
                elif k in ('images', 'comicImages') and v:
                    names.update(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for e in x:
                walk(e)
    for code, _ in LANGS.values():
        for n in CONTENT:
            walk(json.loads((APP / 'assets/content' / f'{n}_{code}.json').read_text(encoding='utf-8')))
    return sorted(names)


def main():
    DATA.mkdir(exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    ICONS.mkdir(parents=True, exist_ok=True)
    for code, _ in LANGS.values():
        for n in CONTENT:
            shutil.copy(APP / 'assets/content' / f'{n}_{code}.json', DATA / f'{n}_{code}.json')
    disc = ios_disclaimers()
    strings = {}
    for lang, (code, values) in LANGS.items():
        s = app_strings(values)
        s['disclaimer'] = disc.get(code) or s['disclaimer_text']
        strings[lang] = s
    (DATA / 'app_strings.json').write_text(json.dumps(strings, ensure_ascii=False, indent=1), encoding='utf-8')

    sizes = {}
    for name in image_names():
        src = next((APP / 'res/drawable-nodpi').glob(name + '.*'))
        im = Image.open(src)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(IMG / f'{name}.webp', 'WEBP', quality=80, method=6)
        for w in SMALL_WIDTHS:
            if w < im.width:
                im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(IMG / f'{name}-{w}.webp', 'WEBP', quality=80, method=6)
        sizes[name] = [im.width, im.height]
    (DATA / 'image_sizes.json').write_text(json.dumps(sizes, indent=0), encoding='utf-8')

    icon = Image.open(APP / 'res/mipmap-xxxhdpi/ic_launcher.png').convert('RGBA')
    for px in (32, 64, 180, 192):
        icon.resize((px, px), Image.LANCZOS).save(ICONS / f'icon-{px}.png', optimize=True)
    icon.save(ICONS / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    total = sum(f.stat().st_size for f in IMG.iterdir())
    print(f'content files: {len(LANGS) * len(CONTENT)}, images: {len(sizes)} ({total // 1024} KB), '
          f'disclaimers from iOS: {len(disc)}')


if __name__ == '__main__':
    main()
