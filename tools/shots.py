"""Full-page screenshots of the built site (light theme) with headless Chrome, empty bottom trimmed.
Needs the local server: python -m http.server 8766 --bind 127.0.0.1 (in dist/). Chrome must run outside the sandbox.
    python tools/shots.py
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PROFILE = r'C:\Users\mango\AppData\Local\Temp\cfs\chprof_site'
TMP = Path(r'C:\Users\mango\AppData\Local\Temp\cfs\shot_tmp.png')
BASE = 'http://127.0.0.1:8766/'
OUT = Path(__file__).resolve().parent.parent / 'screens'
PAGES = [('index', 'главная'), ('dom/tualet', 'статья'), ('checklists/vet-clinic-visit', 'чек-лист'),
         ('srochnye/poisoning', 'срочная'), ('support', 'поддержка')]


FRAME = Path(r'C:\Users\mango\AppData\Local\Temp\cfs\phone_frame.html')


def shot(url, w, out, h=9000):
    TMP.unlink(missing_ok=True)
    win = w
    if w < 500:  # headless Chrome will not make a window this narrow: show the page in an iframe of the phone width
        FRAME.write_text(f'<!doctype html><body style="margin:0;background:#1F4E3D"><iframe src="{url}" '
                         f'style="border:0;display:block;width:{w}px;height:{h}px"></iframe>', encoding='utf-8')
        url, win = FRAME.as_uri(), 500
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--user-data-dir=' + PROFILE, '--no-first-run', '--blink-settings=preferredColorScheme=1',
                    f'--screenshot={TMP}', f'--window-size={win},{h}', url], capture_output=True, timeout=120)
    im = Image.open(TMP).convert('RGB').crop((0, 0, w, h))
    px = im.load()
    W, H = im.size
    bottom = px[W // 2, H - 1]
    y = H - 1
    while y > 0 and all(abs(px[x, y][i] - bottom[i]) < 6 for x in range(0, W, 37) for i in range(3)):
        y -= 1
    im.crop((0, 0, W, min(H, y + 40))).save(out)
    return out


OUT.mkdir(exist_ok=True)
for lang in sys.argv[1:] or ['ru', 'en']:
    for n, (key, name) in enumerate(PAGES, 1):
        for w, dev in ((1280, 'компьютер'), (390, 'телефон')):
            o = shot(f'{BASE}{lang}/{key}.html', w, OUT / f'{lang}_{n}_{name}_{dev}.png')
            print(o.name, Image.open(o).size, flush=True)
