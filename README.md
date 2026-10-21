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
Затем http://127.0.0.1:8766/ (выбор языка) или http://127.0.0.1:8766/ru/index.html.

`BASE_URL` в `tools/build.py` пока пустой: после выбора хостинга вписать адрес — появятся абсолютные `hreflang`,
`canonical`, `og:url` и `sitemap.xml`.
