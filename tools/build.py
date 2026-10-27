"""Builds the Cat First website into dist/: every page in every language, from the app's content (app_data/) and the
site's own texts (src/i18n/<lang>.json). Static files only: no cookies or browser storage, no forms, no external
requests. Language = URL (/ru/, /en/...).
    python tools/build.py
"""
import html
import json
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path

from sync_from_app import SMALL_WIDTHS

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'app_data'
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
BASE_URL = 'https://catfirst.org/'  # absolute hreflang, canonical, og:url and sitemap.xml; '' for relative only
YEAR = 2026
MAIL = 'catfirstsupport@gmail.com'
PLAY = 'https://play.google.com/store/apps/details?id=com.catfirst.app'
APPSTORE = 'https://apps.apple.com/us/app/cat-first/id6811563624'
LANGS = ['ru', 'en', 'uk', 'de', 'es', 'fr', 'it', 'pl', 'pt-br', 'tr', 'kk', 'el', 'sr', 'bs']
CONTENT_CODE = {'pt-br': 'pt'}
PASTELS = ['mint', 'lav', 'peach', 'rose', 'sky', 'sage']
E = html.escape

APP_STR = json.loads((DATA / 'app_strings.json').read_text(encoding='utf-8'))
SIZES = json.loads((DATA / 'image_sizes.json').read_text(encoding='utf-8'))
# how wide each kind of picture is on the page (CSS px): lets the browser pick the right srcset copy
SLOT_SIZES = {'wide': '(max-width: 1023px) 100vw, 700px', 'wide head': '(max-width: 1023px) 100vw, 760px',
              'cell': '(max-width: 767px) 100vw, 340px', 'cover': '(max-width: 767px) 100vw, 580px',
              'frame': '(max-width: 767px) 100vw, 460px'}

P = {  # outline icons, 24x24, stroke = currentColor
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'chev': '<path d="M6 9l6 6 6-6"/>',
    'chevl': '<path d="M15 5l-7 7 7 7"/>',
    'chevr': '<path d="M9 5l7 7-7 7"/>',
    'ok': '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    'no': '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
    'bulb': '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    'alert': '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.5"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.5"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    'lock': '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'home': '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/>',
    'book': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/>',
    'list': '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M4 6l1.5 1.5L8 5M4 12l1.5 1.5L8 11M4 18l1.5 1.5L8 17"/>',
    'aid': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5h8v2M12 10.5v6M9 13.5h6"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'phone': '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 18h2"/>',
    'nocookie': '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
}


def ic(name, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{P[name]}</svg>'


def slug(title):
    """English title -> URL part: 'Injured by a Child: First Aid…' -> 'injured-by-a-child', "Can't…" -> 'cant-…'."""
    title = re.split(r'\s*[:(\u2014]\s*', title)[0].replace("'", '').replace('\u2019', '')
    s = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    while len(s) > 40 and '-' in s:
        s = s.rsplit('-', 1)[0]
    return s


def load(name, lang):
    return json.loads((DATA / f'{name}_{CONTENT_CODE.get(lang, lang)}.json').read_text(encoding='utf-8'))


# Slugs come from the English content; every language has the same items in the same order (checked below).
EN = {n: load(n, 'en') for n in ('safe_home_categories', 'home_articles', 'knowledge', 'checklists', 'emergency')}
DOM_SLUGS = {c['id']: slug(c['title']) for c in EN['safe_home_categories']}
KN_SLUGS = {c['id']: c['id'].replace('_', '-') for c in EN['knowledge']}
CL_SLUGS = [slug(c['title']) for c in EN['checklists']]
EM_SLUGS = [slug(e['title']) for e in EN['emergency']]
assert all(len(set(x)) == len(x) for x in (list(DOM_SLUGS.values()), CL_SLUGS, EM_SLUGS))


def dir_of(lang, key):
    """Folder of a page: every page is <lang>/<key>/index.html, so its address ends with '/' and has no '.html'."""
    parts = [x for x in (lang, key) if x]
    return '/'.join(parts) + '/' if parts else ''


# --- text, like the app's ParagraphText / splitInlineList ------------------------------------------------------------
ITEM_SEP = re.compile(r';\s+')
NUMBERED = re.compile(r'^\d+[.)]\s')


def split_inline(line):
    """'Lead-in: a; b; c' -> lead-in + one bullet per item (only lines with at least two '; ')."""
    t = line.strip()
    if t.startswith('•'):
        return [line]
    parts = ITEM_SEP.split(t)
    if len(parts) < 3:
        return [line]
    lead, first = None, parts[0]
    colon = first.find(': ')
    if 1 <= colon <= 60:
        lead, first = first[:colon + 1], first[colon + 2:]
    items = [first] + parts[1:]
    out = [lead] if lead else []
    for i, item in enumerate(items):
        text = item + ';' if i < len(items) - 1 else item
        out.append(text if NUMBERED.search(text) else '• ' + text)
    return out


def prose(text, split=False):
    lines = (text or '').split('\n')
    if split:
        lines = [x for line in lines for x in split_inline(line)]
    out, bullets, dos = [], [], []

    def flush():
        if bullets:
            out.append('<ul class="dots">' + ''.join(f'<li>{E(b)}</li>' for b in bullets) + '</ul>')
            bullets.clear()
        if dos:
            out.append('<div class="dodont">' + ''.join(
                f'<div class="{"do" if ok else "dont"}">{ic("ok" if ok else "no")}<span>{E(t)}</span></div>'
                for ok, t in dos) + '</div>')
            dos.clear()
    for line in lines:
        s = line.strip()
        if not s:
            flush()
        elif line.startswith('## '):
            flush()
            out.append(f'<h3 class="sub">{E(line[3:].strip())}</h3>')
        elif s.startswith('•'):
            bullets.append(s[1:].strip())
        elif s[0] in '✅❌':
            dos.append((s[0] == '✅', s[1:].strip()))
        else:
            flush()
            out.append(f'<p>{E(s)}</p>')
    flush()
    return ''.join(out)


class Page:
    """One output page: knows its path, so every link and asset is relative (works from file:// and any subfolder)."""

    def __init__(self, lang, key):
        self.lang, self.key = lang, key
        self.dir = dir_of(lang, key)
        self.path = self.dir + 'index.html'
        self.t = I18N.get(lang, {})
        self.a = APP_STR.get(lang, {})
        self.used_imgs = set()

    def url(self, target):
        return posixpath.relpath(target, posixpath.dirname(self.path) or '.')

    def link(self, key, lang=None):
        """Relative address of another page's folder, ending with '/'."""
        rel = posixpath.relpath(dir_of(lang or self.lang, key).rstrip('/') or '.', posixpath.dirname(self.path) or '.')
        return './' if rel == '.' else rel + '/'

    def pic(self, name, alt, cls='wide', lazy=True, sizes=None, priority=False):
        """An <img> with srcset (480 / 800 / full), so a phone or a small slot downloads a smaller copy."""
        if not name or name not in SIZES:
            return ''
        w, h = SIZES[name]
        portrait = h > w * 1.05
        self.used_imgs.add(name)
        srcset = ', '.join([f'{self.url(f"img/{name}-{sw}.webp")} {sw}w' for sw in SMALL_WIDTHS if sw < w] +
                           [f'{self.url(f"img/{name}.webp")} {w}w'])
        sizes = sizes or ('(max-width: 767px) 100vw, 420px' if portrait and cls.startswith('wide') else SLOT_SIZES[cls])
        return (f'<img class="{cls}{" portrait" if portrait else ""}" src="{self.url("img/" + name + ".webp")}" '
                f'srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{E(alt)}"'
                f'{" loading=lazy" if lazy else ""}{" fetchpriority=high" if priority else ""} decoding="async" data-img="{name}">')


def fmt(t, key, **kw):
    return t[key].format(**kw)


# --- shared blocks -----------------------------------------------------------------------------------------------------
def nav_items(pg):
    a, t = pg.a, pg.t
    return [('', t['home']), ('safe-home', a['nav_home_safety']), ('knowledge', a['nav_knowledge']),
            ('checklists', a['nav_checklists']), ('emergency', a['nav_emergency']), ('support', t['support'])]


def lang_switch(pg):
    items = ''.join(
        f'<li><a href="{pg.link(pg.key, l)}" hreflang="{I18N[l]["html_lang"]}" lang="{I18N[l]["html_lang"]}"'
        f'{" aria-current=page" if l == pg.lang else ""}>{E(I18N[l]["lang_name"])}</a></li>' for l in LANGS)
    return (f'<details class="lsw"><summary aria-label="{E(pg.t["language"])}: {E(pg.t["lang_name"])}">'
            f'{ic("globe", "ic sm")}<span>{E(pg.t["lang_short"])}</span>{ic("chev", "ic xs")}</summary><ul>{items}</ul></details>')


def stores(pg):
    """The official badges (src/originals/store_badges.webp, prepared by import_hero.py)."""
    return (f'<div class="stores"><a class="badge" href="{APPSTORE}"><img src="{pg.url("img/badges/app-store.webp")}" '
            f'width="144" height="48" alt="Download on the App Store"></a>'
            f'<a class="badge" href="{PLAY}"><img src="{pg.url("img/badges/google-play.webp")}" '
            f'width="144" height="48" alt="Get it on Google Play"></a></div>')


def disclaimer(pg):
    return (f'<section class="wrap"><div class="note">{ic("info", "ic nic")}<div><b>{E(pg.t["disclaimer_title"])}</b>'
            f'<p>{E(pg.a["disclaimer"])}</p></div></div></section>')


def cta(pg):
    t = pg.t
    return (f'<section class="wrap"><div class="cta"><div><span class="chip light">{ic("phone", "ic sm")}{E(t["cta_chip"])}</span>'
            f'<h2>{E(t["cta_title"])}</h2><p>{E(t["cta_text"])}</p></div>{stores(pg)}</div></section>')


def crumbs(pg, *items):
    parts = [f'<a href="{pg.link("")}">{ic("home", "ic sm")}{E(pg.t["home"])}</a>'] + [
        f'<a href="{pg.link(k)}">{E(t)}</a>' if k else f'<span aria-current="page">{E(t)}</span>' for k, t in items]
    return f'<nav class="crumbs wrap" aria-label="{E(pg.t["breadcrumbs"])}">' + '<span aria-hidden="true">/</span>'.join(parts) + '</nav>'


def hub_hero(pg, chip, title, lead, stats, image):
    st = ''.join(f'<span>{ic(i, "ic sm")}{E(s)}</span>' for i, s in stats)
    return (f'<section class="wrap"><div class="hero-card"><div><span class="chip">{E(chip)}</span><h1>{E(title)}</h1>'
            f'<p class="lead">{E(lead)}</p><div class="stats">{st}</div></div>'
            f'<div class="hero-pic">{pg.pic(image, title, "frame", lazy=False, priority=True)}</div></div></section>')


def row_card(href, icon, k, title, meta, badge='', em=False):
    b = f' <span class="crit">{E(badge)}</span>' if badge else ''
    return (f'<a class="rcard{" em" if em else ""}" href="{href}"><span class="tile {PASTELS[k % 6]}">{ic(icon)}</span>'
            f'<span class="rt"><b>{E(title)}</b><small>{meta}{b}</small></span><span class="go">{ic("arrow", "ic sm")}</span></a>')


def render(pg, title, body, desc, active=None):
    t = pg.t
    nav = ''.join(f'<a href="{pg.link(k)}"{" aria-current=page class=on" if k == active else ""}>{E(l)}</a>'
                  for k, l in nav_items(pg))
    alts = ''.join(f'<link rel="alternate" hreflang="{I18N[l]["html_lang"]}" href="{BASE_URL + dir_of(l, pg.key) if BASE_URL else pg.link(pg.key, l)}">'
                   for l in LANGS)
    root = BASE_URL or posixpath.relpath('.', posixpath.dirname(pg.path)) + '/'
    alts += f'<link rel="alternate" hreflang="x-default" href="{root}">'
    canon = f'<link rel="canonical" href="{BASE_URL}{pg.dir}">' if BASE_URL else ''
    og = (f'<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">'
          f'<meta property="og:description" content="{E(desc)}"><meta property="og:locale" content="{t["og_locale"]}">'
          + (f'<meta property="og:image" content="{BASE_URL}icons/icon-192.png"><meta property="og:url" content="{BASE_URL}{pg.dir}">' if BASE_URL else ''))
    full_title = title if title == 'Cat First' else f'{title} — Cat First'
    script = f'<script src="{pg.url("gallery.js")}" defer></script>' if 'data-gallery' in body else ''
    doc = f'''<!doctype html>
<html lang="{t["html_lang"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#F2EEE6" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#1B1B19" media="(prefers-color-scheme: dark)"><title>{E(full_title)}</title><meta name="description" content="{E(desc)}">
<link rel="icon" href="{pg.url("favicon.ico")}" sizes="48x48"><link rel="icon" type="image/png" href="{pg.url("icons/icon-192.png")}" sizes="192x192">
<link rel="apple-touch-icon" href="{pg.url("icons/icon-180.png")}">{canon}{alts}{og}<link rel="stylesheet" href="{pg.url("style.css")}">{script}</head>
<body><a class="skip" href="#main">{E(t["skip"])}</a>
<header class="top"><div class="wrap row"><a class="logo" href="{pg.link("")}"><img src="{pg.url("icons/icon-64.png")}" width="32" height="32" alt="">Cat First</a>
<nav class="nav" aria-label="{E(t["menu"])}">{nav}</nav>{lang_switch(pg)}
<details class="menu"><summary aria-label="{E(t["menu"])}">{ic("menu")}</summary><nav aria-label="{E(t["menu"])}">{nav}</nav></details></div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap"><div class="row fr"><nav aria-label="Cat First"><a href="{pg.link("")}">{E(pg.a["about_section_title"])}</a><a href="{pg.link("support")}">{E(t["support"])}</a></nav>
<a class="mail" href="mailto:{MAIL}">{ic("mail", "ic sm")}{MAIL}</a></div>
<div class="row fr small"><span>© {YEAR} Cat First · {E(t["hero_chip"])}</span><span>{ic("nocookie", "ic sm")}{E(t["no_cookies"])}</span></div></div></footer>
</body></html>
'''
    out = DIST / pg.path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8')
    PAGES.append(pg)


# --- pages --------------------------------------------------------------------------------------------------------------
def p_index(lang, C):
    pg = Page(lang, '')
    t, a = pg.t, pg.a
    shots = ''.join(
        f'<img class="phone {cls}" src="{pg.url(f"img/hero/phone_{s}.webp")}" srcset="{pg.url(f"img/hero/phone_{s}-280.webp")} 280w, '
        f'{pg.url(f"img/hero/phone_{s}.webp")} 560w" sizes="{sz}" width="560" height="{h}" alt=""'
        f'{" fetchpriority=high" if cls == "mid" else ""}>'
        for s, cls, h, sz in (('profile', 'left', 1041, '(max-width: 767px) 31vw, 190px'),
                              ('home', 'mid', 1073, '(max-width: 767px) 38vw, 230px'),
                              ('article', 'right', 1064, '(max-width: 767px) 31vw, 190px')))
    vals = [('lock', 'mint', 'v1'), ('shield', 'lav', 'v2'), ('globe', 'peach', 'v3'), ('phone', 'sky', 'v4')]
    vcards = ''.join(f'<div class="vcard {c}">{ic(i)}<b>{E(t[k + "_t"])}</b><small>{E(t[k + "_s"])}</small></div>' for i, c, k in vals)
    DC, KN, CL, EM = C['safe_home_categories'], C['knowledge'], C['checklists'], C['emergency']
    topics = [
        ('safe-home', 'home', 'mint', t['dom_title'], fmt(t, 'n_topics', n=len(DC)), [c['title'] for c in DC[1:5]], 'dom_son_lezhanki'),
        ('knowledge', 'book', 'lav', a['knowledge_hub_title'], fmt(t, 'n_articles', n=len(KN)), [c['title'] for c in KN[:4]], 'znanie_povedenie_comic_1'),
        ('checklists', 'list', 'peach', a['nav_checklists'], fmt(t, 'n_lists', n=len(CL)), [c['title'] for c in CL[:4]], 'dom_samovygul_shleyka'),
        ('emergency', 'aid', 'rose', a['nav_emergency'], fmt(t, 'n_situations', n=len(EM)), [e['title'] for e in EM[3:7]], None),
    ]
    tcards = ''.join(
        f'<a class="tcard{" danger" if p is None else ""}" href="{pg.link(h)}">'
        + (pg.pic(p, '', 'cover') if p else f'<div class="tpic {pc}">{ic(icn)}</div>')
        + f'<div class="tb"><span class="chip{" red" if p is None else ""}">{E(n)}</span><h3>{E(ti)}</h3><ul class="dots">'
        + ''.join(f'<li>{E(x)}</li>' for x in ex) + f'</ul><span class="more">{E(t["open_section"])} {ic("arrow", "ic sm")}</span></div></a>'
        for h, icn, pc, ti, n, ex, p in topics)
    chips = ''.join(f'<a class="chip red" href="{pg.link("emergency/" + EM_SLUGS[i])}">{E(EM[i]["title"])}</a>' for i in range(3, 9))
    body = f'''<section class="wrap hero"><div><span class="chip">{E(t["hero_chip"])}</span><h1 class="display">{E(t["hero_title"])}</h1>
<p class="lead">{E(t["hero_lead"])}</p>{stores(pg)}</div>
<div class="phones" role="img" aria-label="{E(t["hero_alt"])}">{shots}</div></section>
<section class="wrap"><h2 class="h2">{E(t["why"])}</h2><div class="grid4">{vcards}</div></section>
<section class="wrap"><div class="shead"><h2 class="h2">{E(t["topics"])}</h2><span class="kicker">{E(t["in_app"])}</span></div><div class="grid2">{tcards}</div></section>
<section class="wrap"><div class="emband">{ic("alert", "ic big red")}<div><h2>{E(a["nav_emergency"])}</h2><p>{E(t["em_lead"])}</p>
<div class="chips">{chips}</div></div><a class="btn ghost" href="{pg.link("emergency")}">{E(t["all_situations"])} {ic("arrow", "ic sm")}</a></div></section>
{disclaimer(pg)}'''
    render(pg, t['hero_title'], body, t['site_desc'], '')


def p_dom(lang, C):
    DC = C['safe_home_categories']
    arts = {x['id']: x for x in C['home_articles']}
    pg = Page(lang, 'safe-home')
    t, a = pg.t, pg.a
    cards = ''.join(row_card(pg.link('safe-home/' + DOM_SLUGS[c['id']]), 'home', k, c['title'],
                             E(fmt(t, 'n_sections', n=len(arts[c['id']]['sections']))) + ' • ' + E(c.get('subtitle') or ''))
                    for k, c in enumerate(DC))
    body = (crumbs(pg, (None, t['dom_title'])) +
            hub_hero(pg, t['dom_chip'], t['dom_title'], a['safe_home_intro'], [('home', fmt(t, 'n_topics', n=len(DC)))], 'dom_bezopasnost_hero') +
            f'<section class="wrap"><div class="grid2 rows">{cards}</div></section>' + cta(pg) + disclaimer(pg))
    render(pg, t['dom_title'], body, a['safe_home_intro'], 'safe-home')

    for k, c in enumerate(DC):
        art = arts[c['id']]
        pg = Page(lang, 'safe-home/' + DOM_SLUGS[c['id']])
        secs = ''
        for i, s in enumerate(art['sections'], 1):
            style = s.get('style')
            cls = {'tip': ' tip', 'warning': ' warn'}.get(style, '')
            label = {'tip': (ic('bulb', 'ic sm'), t['tip']), 'warning': (ic('alert', 'ic sm'), t['warning'])}.get(style)
            lab = f'<span class="slabel">{label[0]}{E(label[1])}</span>' if label else ''
            if s.get('blocks'):
                blocks = s['blocks']
                texts = [b for b in blocks if b.get('text')]
                pics = [b for b in blocks if b.get('image')]
                if pics and len(pics) == len(texts) and all(b.get('text') and b.get('image') for b in blocks):
                    inner = '<div class="tgrid">' + ''.join(
                        f'<figure>{pg.pic(b["image"], s["heading"], "cell")}<figcaption>{prose(b["text"], True)}</figcaption></figure>'
                        for b in blocks) + '</div>'
                else:
                    inner = ''.join((prose(b['text'], True) if b.get('text') else '') +
                                    (pg.pic(b['image'], s['heading']) if b.get('image') else '') for b in blocks)
            else:
                inner = prose(s.get('body'), True) + pg.pic(s.get('image'), s['heading'])
            secs += (f'<details class="sec{cls}" id="s{i}" data-sec open><summary>{num_badge(i, s["heading"])}'
                     f'<h2 class="sh">{E(s["heading"])}</h2>{lab}{ic("chev", "ic sm chev")}</summary><div class="sb">{inner}</div></details>')
        others = [DC[(k + j) % len(DC)] for j in (1, 2, 3)]
        more = ''.join(row_card(pg.link('safe-home/' + DOM_SLUGS[o['id']]), 'home', (k + j) % 6, o['title'], E(o.get('subtitle') or ''))
                       for j, o in enumerate(others, 1))
        body = (crumbs(pg, ('safe-home', t['dom_title']), (None, art['title'])) +
                f'<section class="wrap art-head" data-article="safe-home/{DOM_SLUGS[c["id"]]}"><span class="chip">{E(t["dom_title"])}</span><h1>{E(art["title"])}</h1>'
                f'<p class="lead">{E(art.get("intro") or "")}</p>{pg.pic(art.get("heroImage"), art["title"], "wide head", lazy=False)}</section>' +
                article_body(pg, art['sections'], secs) +
                f'<section class="wrap"><div class="shead"><h2 class="h2">{E(t["more_in_section"])}</h2></div><div class="grid3">{more}</div></section>' +
                disclaimer(pg) + cta(pg))
        render(pg, art['title'], body, art.get('intro') or c.get('subtitle') or art['title'], 'safe-home')


def num_badge(i, heading):
    """The section's number in a circle, unless the heading already starts with its own ('1. ...' in Knowledge)."""
    return '' if NUMBERED.match(heading) else f'<span class="num">{i}</span>'


def article_body(pg, sections, secs):
    toc = ''.join(f'<li><a href="#s{i}">{"" if NUMBERED.match(s["heading"]) else f"{i}. "}{E(s["heading"])}</a></li>'
                  for i, s in enumerate(sections, 1))
    t, a = pg.t, pg.a
    toggle = (f'<button type="button" onclick="var d=document.querySelectorAll(\'details.sec\'),o=![].some.call(d,function(x){{return !x.open}});'
              f'[].forEach.call(d,function(x){{x.open=!o}})">{E(a["generic_collapse"])} / {E(a["generic_expand"])}</button>')
    return (f'<section class="wrap art"><nav class="toc" aria-label="{E(t["contents"])}"><div class="toch"><b>{E(t["contents"])}</b>{toggle}</div>'
            f'<ol>{toc}</ol></nav><div class="secs">{secs}</div></section>')


def p_knowledge(lang, C):
    KN = C['knowledge']
    pg = Page(lang, 'knowledge')
    t, a = pg.t, pg.a
    cards = ''.join(
        f'<a class="kcard{" wide" if i == len(KN) - 1 else ""}" href="{pg.link("knowledge/" + KN_SLUGS[c["id"]])}"><div class="krow">'
        f'<span class="chip soft">{E(fmt(t, "n_sections", n=len(c["sections"])))}</span><span class="tile {PASTELS[i % 6]}">{ic("book")}</span></div>'
        f'<h2 class="h3">{E(c["title"])}</h2><p>{E(c.get("subtitle") or "")}</p><span class="more">{E(t["read"])} {ic("arrow", "ic sm")}</span></a>'
        for i, c in enumerate(KN))
    body = (crumbs(pg, (None, a['knowledge_hub_title'])) +
            hub_hero(pg, t['kn_chip'], a['knowledge_hub_title'], a['knowledge_hub_intro'],
                     [('book', fmt(t, 'n_articles', n=len(KN))), ('list', fmt(t, 'n_sections', n=sum(len(c['sections']) for c in KN)))],
                     'znanie_povedenie_comic_2') +
            f'<section class="wrap"><div class="grid2">{cards}</div></section>' + cta(pg) + disclaimer(pg))
    render(pg, a['knowledge_hub_title'], body, a['knowledge_hub_intro'], 'knowledge')

    for k, c in enumerate(KN):
        pg = Page(lang, 'knowledge/' + KN_SLUGS[c['id']])
        comics = c.get('comicImages') or []
        strip = gallery(pg, comics, c['title']) if comics else ''
        secs = ''
        for i, s in enumerate(c['sections'], 1):
            if s.get('blocks'):
                inner = ''.join(prose(b['text']) if b.get('text') else pg.pic(b.get('image'), s['heading']) for b in s['blocks'])
            else:
                inner = prose(s.get('body')) + ''.join(pg.pic(n, s['heading']) for n in (s.get('images') or []))
            secs += (f'<details class="sec" id="s{i}" data-sec open><summary>{num_badge(i, s["heading"])}'
                     f'<h2 class="sh">{E(s["heading"])}</h2>{ic("chev", "ic sm chev")}</summary><div class="sb">{inner}</div></details>')
        others = [KN[(k + j) % len(KN)] for j in (1, 2, 3)]
        more = ''.join(row_card(pg.link('knowledge/' + KN_SLUGS[o['id']]), 'book', (k + j) % 6, o['title'], E(o.get('subtitle') or ''))
                       for j, o in enumerate(others, 1))
        body = (crumbs(pg, ('knowledge', a['knowledge_hub_title']), (None, c['title'])) +
                f'<section class="wrap art-head" data-article="knowledge/{KN_SLUGS[c["id"]]}"><span class="chip">{E(a["knowledge_hub_title"])}</span><h1>{E(c["title"])}</h1>'
                f'<p class="lead">{E(c.get("intro") or c.get("subtitle") or "")}</p></section>' + strip +
                article_body(pg, c['sections'], secs) +
                f'<section class="wrap"><div class="shead"><h2 class="h2">{E(t["more_in_section"])}</h2></div><div class="grid3">{more}</div></section>' +
                disclaimer(pg) + cta(pg))
        render(pg, c['title'], body, c.get('subtitle') or c['title'], 'knowledge')


def gallery(pg, names, title):
    """One picture at a time, like the app's comic pager: swipe/scroll (works without JS), arrows and dots (gallery.js)."""
    n = len(names)
    slides = ''.join(f'<figure class="gslide">{pg.pic(name, f"{title} ({j}/{n})", "frame", lazy=j > 1, sizes="(max-width: 940px) 100vw, 900px")}</figure>'
                     for j, name in enumerate(names, 1))
    dots = ''.join(f'<button type="button" aria-label="{j} / {n}"></button>' for j in range(1, n + 1))
    return (f'<section class="wrap"><div class="gallery" data-gallery><div class="gtrack" tabindex="0" role="region" '
            f'aria-label="{E(title)}">{slides}</div>'
            f'<button type="button" class="gnav prev" aria-label="{E(pg.t["prev"])}">{ic("chevl")}</button>'
            f'<button type="button" class="gnav next" aria-label="{E(pg.t["next"])}">{ic("chevr")}</button>'
            f'<div class="gdots">{dots}</div></div></section>')


CL_ICONS = ['aid', 'home', 'shield', 'home', 'globe', 'aid', 'shield', 'home', 'aid', 'info']


def p_checklists(lang, C):
    CL = C['checklists']
    pg = Page(lang, 'checklists')
    t, a = pg.t, pg.a
    cards = ''.join(row_card(pg.link('checklists/' + CL_SLUGS[k]), CL_ICONS[k % 10], k, c['title'],
                             f'<em>{E(fmt(t, "n_items", n=sum(len(s["items"]) for s in c["sections"])))}</em> • ' +
                             E(', '.join(i['label'] for s in c['sections'] for i in s['items'])[:90]) + '…')
                    for k, c in enumerate(CL))
    body = (crumbs(pg, (None, a['nav_checklists'])) +
            hub_hero(pg, t['cl_chip'], a['nav_checklists'], t['cl_lead'], [('list', fmt(t, 'n_lists', n=len(CL)))], 'kogtetochka') +
            f'<section class="wrap"><div class="shead"><h2 class="h2">{E(a["checklists_title"])}</h2></div><div class="grid2 rows">{cards}</div></section>' +
            cta(pg) + disclaimer(pg))
    render(pg, a['nav_checklists'], body, t['cl_lead'], 'checklists')

    for k, c in enumerate(CL):
        pg = Page(lang, 'checklists/' + CL_SLUGS[k])
        parts = ''
        if c.get('intro'):
            parts += f'<p class="lead">{E(c["intro"])}</p>'
        if c.get('warning'):
            parts += f'<div class="warnbox">{ic("alert", "ic")}<p>{E(c["warning"])}</p></div>'
        for s in c['sections']:
            items = ''.join(f'<li data-item>{ic("ok", "ic chk")}<span>{E(i["label"])}'
                            + (f'<small>{E(i["note"])}</small>' if i.get('note') else '') + '</span></li>' for i in s['items'])
            head = f'<h2 class="h2">{E(s["heading"])}</h2>' if s.get('heading') else ''
            parts += f'<div class="card clsec" data-sec>{head}<ul class="checklist">{items}</ul></div>'
        if c.get('footerNote'):
            parts += f'<p class="fnote">{E(c["footerNote"])}</p>'
        others = [(j, CL[(k + j) % len(CL)]) for j in (1, 2, 3)]
        more = ''.join(row_card(pg.link('checklists/' + CL_SLUGS[(k + j) % len(CL)]), 'list', (k + j) % 6, o['title'],
                                E(fmt(t, 'n_items', n=sum(len(s['items']) for s in o['sections'])))) for j, o in others)
        body = (crumbs(pg, ('checklists', a['nav_checklists']), (None, c['title'])) +
                f'<section class="wrap art-head narrow" data-article="checklists/{CL_SLUGS[k]}"><span class="chip">{E(a["nav_checklists"])}</span>'
                f'<h1>{E(c["title"])}</h1>{parts}</section>' +
                f'<section class="wrap"><div class="shead"><h2 class="h2">{E(t["more_in_section"])}</h2></div><div class="grid3">{more}</div></section>' +
                disclaimer(pg) + cta(pg))
        render(pg, c['title'], body, c.get('intro') or c['title'], 'checklists')


def alarm(pg):
    a = pg.a
    return (f'<section class="wrap"><div class="alarm" role="note">{ic("alert", "ic big red")}<div><b>{E(a["emergency_banner_title"])}</b>'
            f'<p>{E(a["emergency_banner_body"])}</p></div></div></section>')


def p_emergency(lang, C):
    EM = C['emergency']
    pg = Page(lang, 'emergency')
    t, a = pg.t, pg.a
    cards = ''.join(row_card(pg.link('emergency/' + EM_SLUGS[k]), 'aid', 3, e['title'], '', a['emergency_critical_badge'], em=True)
                    for k, e in enumerate(EM))
    urgent = ''.join(f'<li>{E(u)}</li>' for u in a['emergency_urgent_reasons'])
    body = (crumbs(pg, (None, a['nav_emergency'])) + alarm(pg) +
            f'<section class="wrap"><h1>{E(a["nav_emergency"])}</h1><p class="lead">{E(t["em_lead"])}</p>'
            f'<div class="shead"><h2 class="h2">{E(a["emergency_critical_situations"])}</h2></div>'
            f'<div class="grid2 rows">{cards}</div></section>'
            f'<section class="wrap" id="urgent"><div class="card urgent"><h2 class="h2">{E(a["emergency_urgent_today_title"])}</h2>'
            f'<ul class="bang">{urgent}</ul></div></section>' + disclaimer(pg))
    render(pg, a['nav_emergency'], body, t['em_lead'], 'emergency')

    for k, e in enumerate(EM):
        pg = Page(lang, 'emergency/' + EM_SLUGS[k])
        blocks = ''
        for b in e['blocks']:
            head = f'<h2 class="h2">{E(b["heading"])}</h2>' if b.get('heading') else ''
            blocks += f'<div class="card emblock" data-sec>{head}{prose(b.get("body"))}{pg.pic(b.get("image"), e["title"])}</div>'
        others = [EM[(k + j) % len(EM)] for j in (1, 2, 3)]
        more = ''.join(row_card(pg.link('emergency/' + EM_SLUGS[(k + j) % len(EM)]), 'aid', 3, o['title'], '', a['emergency_critical_badge'], em=True)
                       for j, o in enumerate(others, 1))
        body = (crumbs(pg, ('emergency', a['nav_emergency']), (None, e['title'])) + alarm(pg) +
                f'<section class="wrap art-head narrow" data-article="emergency/{EM_SLUGS[k]}"><span class="chip red">{E(a["emergency_critical_badge"])}</span>'
                f'<h1>{E(e["title"])}</h1>{blocks}'
                f'<p><a class="btn ghost" href="{pg.link("emergency")}#urgent">{E(a["emergency_urgent_today_title"])} {ic("arrow", "ic sm")}</a></p></section>'
                f'<section class="wrap"><div class="shead"><h2 class="h2">{E(t["more_in_section"])}</h2></div><div class="grid3">{more}</div></section>' +
                disclaimer(pg))
        render(pg, e['title'], body, f'{a["nav_emergency"]}: {e["title"]}', 'emergency')


def p_support(lang, C):
    pg = Page(lang, 'support')
    t, a = pg.t, pg.a
    app_path = t['support_app'].format(settings=a['home_settings_link'], section=a['settings_support_section_title'])
    body = (crumbs(pg, (None, t['support'])) +
            f'<section class="wrap"><div class="hero-card support"><div><span class="chip">{ic("mail", "ic sm")}{E(t["support"])}</span>'
            f'<h1>{E(t["support_title"])}</h1><p class="lead">{E(t["support_lead"])}</p>'
            f'<p><a class="btn big" href="mailto:{MAIL}">{ic("mail", "ic")}{MAIL}</a></p>'
            f'<p class="muted">{E(app_path)}</p></div>'
            f'<div class="sup-side"><div class="vcard mint">{ic("nocookie")}<b>{E(t["no_cookies"])}</b><small>{E(t["support_privacy"])}</small></div></div></div></section>' +
            disclaimer(pg))
    render(pg, t['support_title'], body, t['support_lead'], 'support')


def p_root():
    """dist/index.html: opens the version in the browser's language (navigator.languages, read on the device; nothing
    sent or stored), English if none fits; without JS it is a list of the 14 languages."""
    pg = Page(None, '')
    links = ''.join(f'<li><a href="{l}/" hreflang="{I18N[l]["html_lang"]}" lang="{I18N[l]["html_lang"]}">'
                    f'{E(I18N[l]["lang_name"])}</a></li>' for l in LANGS)
    alts = ''.join(f'<link rel="alternate" hreflang="{I18N[l]["html_lang"]}" href="{BASE_URL}{l}/">' for l in LANGS)
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#F2EEE6" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#1B1B19" media="(prefers-color-scheme: dark)"><title>Cat First</title><meta name="description" content="{E(I18N["en"]["site_desc"])}">
<link rel="icon" href="favicon.ico" sizes="48x48"><link rel="icon" type="image/png" href="icons/icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="icons/icon-180.png">{alts}<link rel="stylesheet" href="style.css">
<script>{AUTO_LANG}</script></head>
<body><main class="wrap langpage"><img src="icons/icon-192.png" width="96" height="96" alt=""><h1>Cat First</h1>
<p class="lead">{E(I18N["en"]["choose_lang"])}</p><ul class="langlist">{links}</ul></main></body></html>
'''
    (DIST / 'index.html').write_text(doc, encoding='utf-8')
    PAGES.append(pg)


# languages without their own version that readers usually understand in one of ours
LANG_ALIASES = {'pt': 'pt-br', 'hr': 'bs', 'sh': 'bs'}
AUTO_LANG = ('(function(){var have=' + json.dumps(LANGS) + ',alias=' + json.dumps(LANG_ALIASES) + ','
             'list=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||""];'
             'for(var i=0;i<list.length;i++){var c=String(list[i]).toLowerCase(),p=c.split("-")[0],'
             't=have.indexOf(c)>=0?c:have.indexOf(p)>=0?p:alias[p];if(t){location.replace(t+"/");return}}'
             'location.replace("en/")})();')


def check_order():
    for lang in LANGS:
        for n in ('checklists', 'emergency'):
            icons = [x.get('icon') for x in load(n, lang)]
            assert icons == [x.get('icon') for x in EN[n]], f'{n}_{lang}: items differ from en'
        assert [c['id'] for c in load('safe_home_categories', lang)] == [c['id'] for c in EN['safe_home_categories']]
        assert [c['id'] for c in load('knowledge', lang)] == [c['id'] for c in EN['knowledge']]


I18N = {l: json.loads((SRC / f'i18n/{l}.json').read_text(encoding='utf-8')) for l in LANGS}
PAGES = []


def main():
    check_order()
    DIST.mkdir(exist_ok=True)
    for old in DIST.iterdir():  # empty dist/ but keep the folder itself (a local server may be running in it)
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    shutil.copy(SRC / 'style.css', DIST / 'style.css')
    shutil.copy(SRC / 'gallery.js', DIST / 'gallery.js')
    shutil.copytree(SRC / 'img', DIST / 'img')
    shutil.copytree(SRC / 'hero', DIST / 'img/hero')
    shutil.copytree(SRC / 'badges', DIST / 'img/badges')
    shutil.copytree(SRC / 'icons', DIST / 'icons')
    shutil.move(DIST / 'icons/favicon.ico', DIST / 'favicon.ico')
    (DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\n' + (f'Sitemap: {BASE_URL}sitemap.xml\n' if BASE_URL else ''), encoding='utf-8')
    (DIST / '.nojekyll').write_text('', encoding='utf-8')
    for lang in LANGS:
        C = {n: load(n, lang) for n in EN}
        for f in (p_index, p_dom, p_knowledge, p_checklists, p_emergency, p_support):
            f(lang, C)
    p_root()
    if BASE_URL:
        urls = ''.join(f'<url><loc>{BASE_URL}{p.dir}</loc></url>' for p in PAGES)
        (DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                          + urls + '</urlset>\n', encoding='utf-8')
    used = set().union(*(p.used_imgs for p in PAGES))
    unused = sorted(set(SIZES) - used)
    size = sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file())
    print(f'pages: {len(PAGES)}, languages: {len(LANGS)}, images used: {len(used)}, unused: {unused}, dist: {size // 1024} KB')


if __name__ == '__main__':
    main()
