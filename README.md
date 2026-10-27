# Cat First — сайт

Статический сайт приложения Cat First на 14 языках (`/ru/`, `/en/`, `/uk/`, `/de/`, `/es/`, `/fr/`, `/it/`, `/pl/`,
`/pt-br/`, `/tr/`, `/kk/`, `/el/`, `/sr/`, `/bs/`). Без cookies, хранилища браузера, форм, аналитики и запросов к чужим
доменам; связь — только `mailto:catfirstsupport@gmail.com`. Светлая и тёмная тема — по настройке системы
(тёмные цвета — из палитры приложения), выбор нигде не сохраняется.

## Папки
| Что | Где |
|---|---|
| Генератор страниц | `tools/build.py` |
| Копирование контента, строк и картинок из Android-репозитория | `tools/sync_from_app.py` |
| Телефоны первого экрана и значки магазинов (из `src/originals/`) | `tools/import_hero.py` → `src/hero/`, `src/badges/` |
| Проверка полноты, ссылок и правил | `tools/check.py` |
| Снимки страниц (Chrome без окна) | `tools/shots.py` → `screens/` |
| Тексты интерфейса сайта по языкам | `src/i18n/<язык>.json` |
| Стили | `src/style.css` |
| Копия контента и строк приложения | `app_data/` |
| Готовый сайт | `dist/` |
| Прототип и его генератор (для справки) | `prototype/`, `tools/prototype_gen_site.py` |

## Пересобрать
```
python tools/sync_from_app.py   # если в приложении поменялись статьи, строки или картинки
python tools/build.py
python tools/check.py
```

## Открыть локально
```
cd dist
python -m http.server 8766 --bind 127.0.0.1
```
Затем http://127.0.0.1:8766/ — откроется версия на языке браузера (без JS — список языков), или сразу
http://127.0.0.1:8766/ru/. Адреса страниц — папки без `.html`: `/ru/safe-home/litter-box/`, `/de/emergency/poisoning/`;
имена статей — из английских названий (`slug()` в `build.py`), одинаковые на всех языках.

## Публикация
Адрес сайта — https://catfirst.org/ (`BASE_URL` в `tools/build.py`: из него полные адреса `hreflang`, `canonical`,
`og:url`, `sitemap.xml`). Домен куплен в Cloudflare Registrar; записи DNS для сайта — только «DNS only» (серое облачко),
иначе Cloudflare добавит свою cookie и скрипт.

Каждый push в `main` запускает `.github/workflows/pages.yml`: GitHub собирает сайт (`build.py`), проверяет
(`check.py`) и публикует `dist/` в GitHub Pages. Если проверка не прошла, публикации нет.
