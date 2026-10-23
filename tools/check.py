"""Checks dist/: completeness against the app's content per language, links, external requests, forbidden things.
    python tools/check.py            -> prints a report, exit code 1 on any problem
"""
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, unquote

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
DATA = ROOT / 'app_data'
sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402  (slugs, languages, split_inline)

ALLOWED_HOSTS = {'play.google.com', 'apps.apple.com'}
APP_RES = Path('C:/Users/mango/AndroidStudioProjects/Cat_First-Android/app/src/main/res')
VALUES = {'ru': 'values-ru', 'en': 'values', 'pt-br': 'values-pt-rBR'}
problems = []


def norm(s):
    return re.sub(r'[\s•;#]+', '', html.unescape(s))


def page_text(doc):
    doc = re.sub(r'<(script|style)\b.*?</\1>', '', doc, flags=re.S)
    return norm(re.sub(r'<[^>]+>', '', doc))


def expected(lang):
    """Per section kind: articles, sections, items, images, text lines (for the text check)."""
    L = lambda n: build.load(n, lang)  # noqa: E731
    exp = {}
    arts = {a['id']: a for a in L('home_articles')}
    rows = []
    for c in L('safe_home_categories'):
        a = arts[c['id']]
        # like the app: a section with blocks shows the blocks' pictures, its own 'image' only when it has no blocks
        imgs = [a.get('heroImage')] + [s.get('image') for s in a['sections'] if not s.get('blocks')] + \
            [b.get('image') for s in a['sections'] for b in (s.get('blocks') or [])]
        texts = [a['title'], a.get('intro')] + [x for s in a['sections'] for x in [s['heading'], s.get('body')] + [b.get('text') for b in (s.get('blocks') or [])]]
        rows.append((f'dom/{c["id"]}', len(a['sections']), 0, [i for i in imgs if i], texts))
    exp['dom'] = rows
    rows = []
    for c in L('knowledge'):
        imgs = list(c.get('comicImages') or []) + [i for s in c['sections'] for i in (s.get('images') or []) if not s.get('blocks')] + \
            [b.get('image') for s in c['sections'] for b in (s.get('blocks') or [])]
        texts = [c['title'], c.get('intro') or c.get('subtitle')] + [x for s in c['sections'] for x in
                                                                     [s['heading']] + ([b.get('text') for b in s['blocks']] if s.get('blocks') else [s.get('body')])]
        rows.append((f'znaniya/{c["id"]}', len(c['sections']), 0, [i for i in imgs if i], texts))
    exp['znaniya'] = rows
    rows = []
    for k, c in enumerate(L('checklists')):
        texts = [c['title'], c.get('intro'), c.get('warning'), c.get('footerNote')] + \
            [x for s in c['sections'] for x in [s.get('heading')] + [y for i in s['items'] for y in (i['label'], i.get('note'))]]
        rows.append((f'checklists/{build.CL_SLUGS[k]}', len(c['sections']), sum(len(s['items']) for s in c['sections']), [], texts))
    exp['checklists'] = rows
    rows = []
    for k, e in enumerate(L('emergency')):
        texts = [e['title']] + [x for b in e['blocks'] for x in (b.get('heading'), b.get('body'))]
        rows.append((f'srochnye/{build.EM_SLUGS[k]}', len(e['blocks']), 0, [b['image'] for b in e['blocks'] if b.get('image')], texts))
    exp['srochnye'] = rows
    return exp


def check_completeness():
    table = []
    totals = defaultdict(int)
    for lang in build.LANGS:
        exp = expected(lang)
        row = {'lang': lang}
        for kind, rows in exp.items():
            got = {'articles': 0, 'sections': 0, 'items': 0, 'images': 0}
            want = {'articles': len(rows), 'sections': 0, 'items': 0, 'images': 0}
            for key, nsec, nitems, imgs, texts in rows:
                f = DIST / lang / f'{key}.html'
                if not f.exists():
                    problems.append(f'{lang}: missing page {key}')
                    continue
                doc = f.read_text(encoding='utf-8')
                main = doc.split('<main', 1)[1].split('</main>', 1)[0]
                got['articles'] += main.count('data-article=')
                got['sections'] += main.count(' data-sec')
                got['items'] += main.count(' data-item')
                got['images'] += len(re.findall(r'data-img="', main))
                want['sections'] += nsec
                want['items'] += nitems
                want['images'] += len(imgs)
                missing_imgs = set(imgs) - set(re.findall(r'data-img="([^"]+)"', main))
                if missing_imgs:
                    problems.append(f'{lang}/{key}: images not shown {sorted(missing_imgs)}')
                body = page_text(main)
                for t in texts:
                    for line in (t or '').split('\n'):
                        n = norm(line)
                        if n and n not in body:
                            problems.append(f'{lang}/{key}: text missing: {line[:60]!r}')
            for m in want:
                if got[m] != want[m]:
                    problems.append(f'{lang}/{kind}: {m} on site {got[m]} != in JSON {want[m]}')
                totals[(kind, m)] += got[m]
            row[kind] = got
        table.append(row)
    return table


ATTR = re.compile(r'\b(href|src)="([^"]*)"')
SRCSET = re.compile(r'\bsrcset="([^"]*)"')


def check_links_and_rules():
    files = list(DIST.rglob('*.html'))
    ids_cache = {}
    my_cat = set()
    for lang in build.LANGS:
        xml = (APP_RES / VALUES.get(lang, 'values-' + lang) / 'strings.xml').read_text(encoding='utf-8')
        my_cat.add(re.search(r'<string name="nav_my_cat">(.*?)</string>', xml).group(1))
    external = defaultdict(int)
    nlinks = 0
    for f in files:
        doc = f.read_text(encoding='utf-8')
        for bad in ('<form', '<input', '<textarea', '<select', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie',
                    '<iframe', '<embed', '<object', '@import', 'url(http'):
            if bad in doc:
                problems.append(f'{f.relative_to(DIST)}: contains {bad}')
        for label in my_cat:  # the app section as a UI element (a link, heading or card), not the words inside an article
            if re.search(rf'>\s*{re.escape(label)}\s*<', doc):
                problems.append(f'{f.relative_to(DIST)}: mentions "{label}"')
        refs = ATTR.findall(doc) + [('src', part.split()[0]) for ss in SRCSET.findall(doc) for part in ss.split(',')]
        for attr, url in refs:
            nlinks += 1
            u = urlsplit(url)
            if u.scheme in ('http', 'https'):
                external[u.hostname] += 1
                if u.hostname not in ALLOWED_HOSTS or attr == 'src':
                    problems.append(f'{f.relative_to(DIST)}: external {attr} {url}')
                continue
            if u.scheme == 'mailto':
                if u.path != build.MAIL:
                    problems.append(f'{f.relative_to(DIST)}: mailto {url}')
                continue
            if u.scheme:
                problems.append(f'{f.relative_to(DIST)}: scheme {url}')
                continue
            target = (f.parent / unquote(u.path)).resolve() if u.path else f
            if not target.exists():
                problems.append(f'{f.relative_to(DIST)}: broken {url}')
                continue
            if u.fragment and target.suffix == '.html':
                if target not in ids_cache:
                    ids_cache[target] = set(re.findall(r'\bid="([^"]+)"', target.read_text(encoding='utf-8')))
                if u.fragment not in ids_cache[target]:
                    problems.append(f'{f.relative_to(DIST)}: missing anchor {url}')
    for js in DIST.rglob('*.js'):
        src = js.read_text(encoding='utf-8')
        for bad in ('localStorage', 'sessionStorage', 'indexedDB', 'cookie', 'fetch(', 'XMLHttpRequest', 'http:', 'https:', 'sendBeacon'):
            if bad in src:
                problems.append(f'{js.relative_to(DIST)}: contains {bad}')
    for css in DIST.rglob('*.css'):
        if re.search(r'url\(|@import', css.read_text(encoding='utf-8')):
            problems.append(f'{css.relative_to(DIST)}: url()/@import')
    return len(files), nlinks, dict(external)


def main():
    table = check_completeness()
    nfiles, nlinks, external = check_links_and_rules()
    print('Completeness (site = JSON per language unless listed under problems):')
    print('lang   | Дом: статей/разделов/картинок | Знания: статей/разделов/картинок | Чек-листы: списков/разделов/пунктов | Срочные: ситуаций/блоков/картинок')
    for r in table:
        d, k, c, s = r['dom'], r['znaniya'], r['checklists'], r['srochnye']
        print(f"{r['lang']:6} | {d['articles']}/{d['sections']}/{d['images']} | {k['articles']}/{k['sections']}/{k['images']} | "
              f"{c['articles']}/{c['sections']}/{c['items']} | {s['articles']}/{s['sections']}/{s['images']}")
    print(f'HTML files: {nfiles}, links and sources checked: {nlinks}, external links: {external}')
    if problems:
        print(f'PROBLEMS: {len(problems)}')
        for p in problems[:80]:
            print(' -', p)
        sys.exit(1)
    print('OK: no problems')


if __name__ == '__main__':
    main()
