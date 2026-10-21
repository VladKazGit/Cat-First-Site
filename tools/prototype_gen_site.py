"""Design prototype of the Cat First website (Stitch style, our rules): static pages from the app's real content.
No external requests, no cookies/storage, no forms. Output: Desktop/Cat First/Дизайн_сайта/."""
import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
APP = Path('C:/Users/mango/AndroidStudioProjects/Cat_First-Android/app/src/main')
OUT = Path('C:/Users/mango/Desktop/Cat First/Дизайн_сайта')
IMG = OUT / 'img'
IMG.mkdir(parents=True, exist_ok=True)
E = html.escape


def load(name):
    return json.load(open(APP / 'assets/content' / f'{name}_ru.json', encoding='utf-8'))


def img(name):
    """Copies a drawable into img/ and returns its path, or None."""
    if not name or name == 'None':
        return None
    for f in (APP / 'res/drawable-nodpi').glob(name + '.*'):
        shutil.copy(f, IMG / f.name)
        return 'img/' + f.name
    return None


DOM_CATS = load('safe_home_categories')
DOM = {a['id']: a for a in load('home_articles')}
KN = load('knowledge')
CL = load('checklists')
EM = load('emergency')
STR = open(APP / 'res/values-ru/strings.xml', encoding='utf-8').read()
URGENT = re.findall(r'<item>(.*?)</item>', re.search(r'<string-array name="emergency_urgent_reasons">(.*?)</string-array>', STR, re.S).group(1))
DISCLAIMER = ('Информация в приложении собрана из открытых источников и опыта владельцев кошек. Она не заменяет '
              'консультацию и осмотр у ветеринара. Решения о здоровье и уходе за питомцем принимает владелец — при любых '
              'сомнениях обратитесь к ветеринару.')
PLAY = 'https://play.google.com/store/apps/details?id=com.catfirst.app'
APPSTORE = 'https://apps.apple.com/us/app/cat-first/id6811563624'
PASTELS = ['mint', 'lav', 'peach', 'rose', 'sky', 'sage']

P = {  # outline icons, 24x24, stroke = currentColor
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'chev': '<path d="M6 9l6 6 6-6"/>',
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
    'paw': '<circle cx="6.5" cy="10" r="1.7"/><circle cx="10" cy="6" r="1.7"/><circle cx="14" cy="6" r="1.7"/><circle cx="17.5" cy="10" r="1.7"/><path d="M8 17c0-3 2-5.5 4-5.5s4 2.5 4 5.5c0 1.6-1.6 2.3-4 2.3s-4-.7-4-2.3z"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'print': '<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="8" rx="2"/><path d="M7 14h10v6H7z"/>',
    'phone': '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 18h2"/>',
    'cat': '<path d="M5 20V9l2.5-5 2.5 4h4l2.5-4L19 9v11z"/><path d="M9.5 13v.5M14.5 13v.5M10.5 16.5h3"/>',
    'play': '<path d="M6 4l13 8-13 8z"/>',
    'apple': '<path d="M15.5 4.5c-.2 1.3-1 2.5-2.6 2.8M16.6 9.2c-1.6-1-3-.8-4.6 0-1.6-.8-3-1-4.6 0-2.4 1.6-2 6 .1 9 1 1.5 2 2 3 1.7 1-.3 2-.3 3 0 1 .3 2-.2 3-1.7.8-1.2 1.3-2.4 1.5-3.4-1.7-.8-2.4-2.3-1.4-5.6z"/>',
    'nocookie': '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
}


def ic(name, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{P[name]}</svg>'


NAV = [('dom.html', 'Дом'), ('znaniya.html', 'Знания'), ('checklists.html', 'Чек-листы'), ('srochnye.html', 'Срочные ситуации'), ('#', 'Поддержка')]


def page(file, title, body, active=''):
    nav = ''.join(f'<a href="{h}"{" class=on" if l == active else ""}>{l}</a>' for h, l in NAV)
    langs = ''.join(f'<a href="#">{c}</a>' for c in ('RU', 'EN', 'UK', 'DE', 'ES', 'FR', 'IT', '…'))
    doc = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} — Cat First</title><meta name="description" content="Cat First — спокойная забота о кошке."><link rel="stylesheet" href="style.css"></head>
<body><header class="top"><div class="wrap row"><a class="logo" href="index.html">{ic('cat','ic logo-ic')}Cat First</a>
<nav class="nav">{nav}</nav><div class="langs">{ic('globe','ic sm')}{langs}</div>
<details class="menu"><summary aria-label="Меню"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary><nav>{nav}</nav></details></div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap"><div class="row fr"><nav><a href="#">Политика конфиденциальности</a><a href="#">Поддержка</a><a href="index.html">О приложении</a></nav>
<a class="mail" href="mailto:catfirstsupport@gmail.com">{ic('mail','ic sm')}catfirstsupport@gmail.com</a></div>
<div class="row fr small"><span>© 2026 Cat First · Для заботливых владельцев</span><span>{ic('nocookie','ic sm')}Без cookies и сбора данных</span></div></div></footer>
</body></html>'''
    (OUT / file).write_text(doc, encoding='utf-8')


def stores(dark=False):
    c = 'store dark' if dark else 'store'
    return (f'<div class="stores"><a class="{c}" href="{PLAY}">{ic("play")}<span><small>Доступно в</small>Google Play</span></a>'
            f'<a class="{c}" href="{APPSTORE}">{ic("apple")}<span><small>Загрузите в</small>App Store</span></a></div>')


def disclaimer():
    return f'<section class="wrap"><div class="note">{ic("info","ic nic")}<div><b>Не заменяет ветеринара</b><p>{E(DISCLAIMER)}</p></div></div></section>'


def cta(title, text):
    return (f'<section class="wrap"><div class="cta"><div><span class="chip light">{ic("phone","ic sm")}Всегда под рукой</span>'
            f'<h2>{title}</h2><p>{text}</p></div>{stores()}</div></section>')


def crumbs(*items):
    parts = [f'<a href="index.html">{ic("home","ic sm")}Главная</a>'] + [f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>' for h, t in items]
    return '<nav class="crumbs wrap">' + ' / '.join(parts) + '</nav>'


def hub_hero(chip, title, lead, stats, image):
    st = ''.join(f'<span>{ic(i,"ic sm")}{E(t)}</span>' for i, t in stats)
    pic = f'<img src="{image}" alt="">' if image else ''
    return (f'<section class="wrap"><div class="hero-card"><div><span class="chip">{E(chip)}</span><h1>{E(title)}</h1>'
            f'<p class="lead">{E(lead)}</p><div class="stats">{st}</div></div><div class="hero-pic">{pic}</div></div></section>')


def row_card(href, icon, k, title, meta, badge=''):
    b = f' <span class="badge">{E(badge)}</span>' if badge else ''
    return (f'<a class="rcard" href="{href}"><span class="tile {PASTELS[k % 6]}">{ic(icon)}</span>'
            f'<span class="rt"><b>{E(title)}{b}</b><small>{meta}</small></span><span class="go">{ic("arrow","ic sm")}</span></a>')


# --- body text: paragraphs, bullet lines and "✅ / ❌" pairs ------------------------------------------------------
def text_html(text):
    out, items, dos = [], [], []

    def flush():
        if items:
            out.append('<ul class="dots">' + ''.join(f'<li>{E(i)}</li>' for i in items) + '</ul>'); items.clear()
        if dos:
            out.append('<div class="dodont">' + ''.join(
                f'<div class="{"do" if ok else "dont"}">{ic("ok" if ok else "no")}<span>{E(t)}</span></div>' for ok, t in dos) + '</div>'); dos.clear()
    for line in text.split('\n'):
        s = line.strip()
        if not s:
            flush(); continue
        if s[0] in '✅❌':
            dos.append((s[0] == '✅', s[1:].strip()))
        elif s[0] in '•-—' and len(s) > 2:
            items.append(s[1:].strip())
        else:
            flush(); out.append(f'<p>{E(s)}</p>')
    flush()
    return ''.join(out)


def section_body(sec):
    blocks = sec.get('blocks')
    if blocks:
        texts = [b['text'] for b in blocks if b.get('text')]
        pics = [img(b['image']) for b in blocks if b.get('image')]
        pics = [p for p in pics if p]
        if pics and len(pics) == len(texts):  # one picture per paragraph: a card grid (e.g. litter types)
            return '<div class="tgrid">' + ''.join(
                f'<figure><img src="{p}" alt=""><figcaption>{text_html(t)}</figcaption></figure>' for t, p in zip(texts, pics)) + '</div>'
        return ''.join(text_html(b['text']) if b.get('text') else (f'<img class="wide" src="{img(b["image"])}" alt="">' if img(b.get('image')) else '') for b in blocks)
    body = text_html(sec.get('body', ''))
    p = img(sec.get('image'))
    return body + (f'<img class="wide" src="{p}" alt="">' if p else '')


# --- pages --------------------------------------------------------------------------------------------------------
def index():
    topics = [
        ('dom.html', 'home', 'mint', 'Безопасный дом', f'{len(DOM_CATS)} тем', [c['title'] for c in DOM_CATS[1:5]], img('dom_son_lezhanki')),
        ('znaniya.html', 'book', 'lav', 'База знаний', f'{len(KN)} больших статей', [c['title'] for c in KN[:4]], img('znanie_povedenie_comic_1')),
        ('checklists.html', 'list', 'peach', 'Чек-листы', f'{len(CL)} списков', [c['title'] for c in CL[:4]], img('dom_samovygul_shleyka')),
        ('srochnye.html', 'aid', 'rose', 'Срочные ситуации', f'{len(EM)} ситуаций', [c['title'] for c in EM[3:7]], None),
    ]
    tcards = ''.join(
        f'<a class="tcard{" danger" if i == 3 else ""}" href="{h}">' + (f'<img src="{p}" alt="">' if p else f'<div class="tpic {pc}">{ic(icn)}</div>') +
        f'<div class="tb"><span class="chip {"red" if i == 3 else ""}">{E(n)}</span><h3>{E(t)}</h3><ul class="dots">' +
        ''.join(f'<li>{E(x)}</li>' for x in ex) + f'</ul><span class="more">Открыть раздел {ic("arrow","ic sm")}</span></div></a>'
        for i, (h, icn, pc, t, n, ex, p) in enumerate(topics))
    vals = [('lock', 'mint', 'Без регистрации', 'Ни аккаунта, ни пароля'), ('shield', 'lav', 'Без рекламы и слежки', 'Ничего не собираем'),
            ('globe', 'peach', '14 языков', 'От русского до греческого'), ('phone', 'sky', 'Android и iPhone', 'Одно приложение — два магазина')]
    vcards = ''.join(f'<div class="vcard {c}">{ic(i)}<b>{E(t)}</b><small>{E(s)}</small></div>' for i, c, t, s in vals)
    chips = ''.join(f'<span class="chip red">{E(e["title"])}</span>' for e in EM[3:9])
    news = ['Новые статьи: пожилая кошка, если не можете оставить кошку у себя, аллергия, дети и кошки',
            'В «Срочных ситуациях» — что делать, если ребёнок травмировал кошку', 'В «Доме» — картинки ко всем видам наполнителя',
            'Новые языки: греческий, сербский и боснийский', 'Поиск по «Знаниям» и «Дому»']
    body = f'''<section class="wrap hero"><div><span class="chip">Для заботливых владельцев</span><h1 class="display">Спокойная забота о кошке</h1>
<p class="lead">Советы для безопасного дома, база знаний, чек-листы и первая помощь в срочных ситуациях. Без регистрации и рекламы.</p>{stores()}</div>
<div class="hero-pic big"><img src="{img('dom_bezopasnost_hero')}" alt="Кошка дома"></div></section>
<section class="wrap"><h2 class="h2">Почему Cat First</h2><div class="grid4">{vcards}</div></section>
<section class="wrap"><div class="shead"><h2 class="h2">Темы</h2><span class="kicker">Всё это есть и в приложении</span></div><div class="grid2">{tcards}</div></section>
<section class="wrap"><div class="emband">{ic('alert','ic big red')}<div><h2>Срочные ситуации</h2><p>Пошаговые действия, когда важна каждая минута, и признаки, при которых нужно к врачу сегодня.</p>
<div class="chips">{chips}</div></div><a class="btn ghost" href="srochnye.html">Все {len(EM)} ситуаций {ic('arrow','ic sm')}</a></div></section>
<section class="wrap"><div class="card news"><span class="chip">Версия 1.2</span><h2 class="h2">Что нового</h2><ul class="dots">{"".join(f"<li>{E(n)}</li>" for n in news)}</ul></div></section>
{disclaimer()}'''
    page('index.html', 'Спокойная забота о кошке', body)


def hub_dom():
    cards = ''.join(row_card('dom-tualet.html' if c['id'] == 'tualet' else '#', 'home', k, c['title'],
                             f'{len(DOM.get(c["id"], {}).get("sections", []))} разделов • {E(c.get("subtitle") or "")}')
                    for k, c in enumerate(DOM_CATS))
    body = (crumbs((None, 'Безопасный дом')) + hub_hero('Уют и безопасность', 'Безопасный дом', 'Как сделать дом удобным и безопасным для кошки — по темам.',
            [('home', f'{len(DOM_CATS)} тем'), ('book', 'Картинки и советы'), ('print', 'Удобно читать')], img('dom_bezopasnost_hero')) +
            f'<section class="wrap"><div class="shead"><h2 class="h2">Темы раздела</h2></div><div class="grid2 rows">{cards}</div></section>' +
            cta('Эти статьи есть и в приложении Cat First', 'Под рукой в любой момент — даже без интернета.') + disclaimer())
    page('dom.html', 'Безопасный дом', body, 'Дом')


def hub_kn():
    cards = ''.join(
        f'<a class="kcard{" wide" if i == len(KN) - 1 else ""}" href="#"><div class="krow"><span class="chip soft">{len(c["sections"])} разделов</span>'
        f'<span class="tile {PASTELS[i % 6]}">{ic("book")}</span></div><h3>{E(c["title"])}</h3><p>{E(c.get("subtitle") or "")}</p>'
        f'<span class="more">Читать статью {ic("arrow","ic sm")}</span></a>' for i, c in enumerate(KN))
    body = (crumbs((None, 'База знаний')) + hub_hero('Энциклопедия заботы', 'База знаний', 'Ваш путеводитель по миру кошек.',
            [('book', f'{len(KN)} больших статей'), ('list', f'{sum(len(c["sections"]) for c in KN)} разделов')], img('znanie_povedenie_comic_2')) +
            f'<section class="wrap"><div class="grid2">{cards}</div></section>' +
            cta('Эти статьи есть и в приложении Cat First', 'Под рукой в любой момент — даже без интернета.') + disclaimer())
    page('znaniya.html', 'База знаний', body, 'Знания')


def hub_cl():
    icons = ['aid', 'paw', 'paw', 'home', 'globe', 'aid', 'shield', 'home', 'aid', 'info']
    cards = ''.join(row_card('#', icons[k % 10], k, c['title'],
                             f'<em>{sum(len(s["items"]) for s in c["sections"])} пунктов</em> • ' +
                             E(', '.join(i['label'] for s in c['sections'] for i in s['items'])[:70]) + '…')
                    for k, c in enumerate(CL))
    first = CL[0]
    items = ''.join(f'<li>{ic("ok","ic chk")}<span>{E(i["label"])}' + (f'<small>{E(i["note"])}</small>' if i.get('note') else '') + '</span></li>'
                    for s in first['sections'] for i in s['items'])
    body = (crumbs((None, 'Чек-листы')) + hub_hero('Списки и памятки', 'Чек-листы', 'Ничего не забыть в важные моменты.',
            [('list', f'{len(CL)} списков'), ('print', 'Готовы к печати')], img('kogtetochka')) +
            f'<section class="wrap"><div class="shead"><h2 class="h2">Тематические памятки</h2></div><div class="grid2 rows">{cards}</div></section>' +
            f'<section class="wrap"><div class="shead"><h2 class="h2">Пример: {E(first["title"])}</h2><a class="btn ghost" href="#">{ic("print","ic sm")}Распечатать</a></div>'
            f'<div class="card"><ul class="checklist">{items}</ul></div></section>' +
            cta('Все чек-листы — в приложении Cat First', 'Под рукой в любой момент — даже без интернета.') + disclaimer())
    page('checklists.html', 'Чек-листы', body, 'Чек-листы')


def hub_em():
    cards = ''.join(row_card('#', 'aid', 3, e['title'], '<span class="crit">КРИТИЧНО</span>') for e in EM)
    urgent = ''.join(f'<li>{E(u)}</li>' for u in URGENT)
    body = (crumbs((None, 'Срочные ситуации')) +
            f'<section class="wrap"><div class="alarm">{ic("alert","ic big red")}<div><b>Экстренная ситуация?</b><p>Не тратьте время на чтение, если животное не дышит или без сознания. Немедленно звоните врачу.</p></div></div></section>'
            f'<section class="wrap"><h1>Срочные ситуации</h1><p class="lead">{len(EM)} пошаговых инструкций первой помощи.</p><div class="shead"><h2 class="h2">Критичные ситуации</h2></div>'
            f'<div class="grid2 rows em">{cards}</div></section>'
            f'<section class="wrap"><div class="card urgent"><h2 class="h2">Когда к врачу СЕГОДНЯ (не ждать)</h2><ul class="bang">{urgent}</ul></div></section>' + disclaimer())
    page('srochnye.html', 'Срочные ситуации', body, 'Срочные ситуации')


def article():
    a = DOM['tualet']
    toc = ''.join(f'<li><a href="#s{i}">{i}. {E(s["heading"])}</a></li>' for i, s in enumerate(a['sections'], 1))
    secs = ''
    for i, s in enumerate(a['sections'], 1):
        cls = {'tip': ' tip', 'warning': ' warn'}.get(s.get('style'), '')
        badge = {'tip': ic('bulb', 'ic sm'), 'warning': ic('alert', 'ic sm')}.get(s.get('style'), '')
        secs += (f'<details class="sec{cls}" id="s{i}" open><summary><span class="num">{i}</span><b>{badge}{E(s["heading"])}</b>{ic("chev","ic sm chev")}</summary>'
                 f'<div class="sb">{section_body(s)}</div></details>')
    others = ''.join(row_card('#', 'home', k, c['title'], E(c.get('subtitle') or '')) for k, c in enumerate(x for x in DOM_CATS if x['id'] in ('opasnosti', 'eda_i_voda', 'cvety')))
    body = (crumbs(('dom.html', 'Безопасный дом'), (None, a['title'])) +
            f'<section class="wrap art-head"><span class="chip">Безопасный дом</span><h1>{E(a["title"])}</h1><p class="lead">{E(a["intro"])}</p></section>'
            f'<section class="wrap art"><aside class="toc"><div class="toch"><b>Содержание</b><button type="button" onclick="document.querySelectorAll(\'details.sec\').forEach(d=>d.open=!d.open)">Свернуть / развернуть</button></div><ol>{toc}</ol></aside>'
            f'<div class="secs">{secs}</div></section>'
            f'<section class="wrap"><div class="shead"><h2 class="h2">Другие темы раздела</h2></div><div class="grid3">{others}</div></section>' +
            disclaimer() + cta('Эти статьи есть и в приложении Cat First', 'Под рукой в любой момент — даже без интернета.'))
    page('dom-tualet.html', a['title'], body, 'Дом')


for f in (index, hub_dom, hub_kn, hub_cl, hub_em, article):
    f()
print('pages:', sorted(p.name for p in OUT.glob('*.html')), 'images:', len(list(IMG.iterdir())))
