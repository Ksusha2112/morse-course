# Курсовой проект: Азбука Морзе

Микросервисное приложение для преобразования текста с помощью азбуки Морзе.
Курс «Современные технологии программирования», задание 06.

## Возможности

- Кодирование текста (латиница, кириллица, цифры, знаки) в азбуку Морзе и обратно
- Загрузка текста из файла (UTF-8 / CP1251)
- Экспорт результата в TXT, CSV и PDF
- Общая статистика переводов (сохраняется в SQLite)
- Веб-интерфейс с переключением режимов

## Архитектура

```
[frontend (nginx :8080)]
        |  /api/    -> [backend (FastAPI :8000)]  -- кодирование/декодирование
        |  /stats/  -> [stats   (FastAPI :8003)]  -- счётчики (SQLite)
        |  /export/ -> [export  (FastAPI :8004)]  -- TXT / CSV / PDF
```

## Запуск

### Вариант 1 — всё сразу без Docker (одной командой)

```bash
python run_dev.py
```

Скрипт поднимает все три сервиса, дожидается готовности и открывает Swagger UI
в браузере. Остановка — Ctrl+C. В PyCharm достаточно открыть `run_dev.py`
и нажать ▶ (зелёный треугольник).

Альтернативы: `run_all.bat` (Windows, сервисы в отдельных окнах) и
`./run_all.sh` (Linux/macOS).

### Вариант 2 — Docker

```bash
docker compose up --build
```

Полный стек, включая фронтенд: http://localhost:8080

### Адреса сервисов

- Swagger UI бэкенда: http://localhost:8000/docs
- Swagger UI статистики: http://localhost:8003/docs
- Swagger UI экспорта: http://localhost:8004/docs
- Веб-интерфейс (Docker): http://localhost:8080

## Тесты

В каждом сервисе есть набор unit- и API-тестов (pytest):

```bash
# backend
cd backend
pip install -r requirements-dev.txt
pytest

# stats-service
cd ../stats-service
pip install -r requirements-dev.txt
pytest

# export-service
cd ../export-service
pip install -r requirements-dev.txt
pytest
```

Что покрывают тесты:

- **backend**: таблица Морзе (encode/decode, round-trip, неизвестные символы),
  все эндпоинты API (успешные ответы, 400/413/422, загрузка файлов UTF-8 и CP1251),
  вызов статистики.
- **stats-service**: инкремент счётчиков, накопление, некорректные запросы, health.
- **export-service**: генерация TXT/CSV/PDF, ошибки формата, health.

CI (GitHub Actions, `.github/workflows/tests.yml`) запускает все три набора тестов
при каждом push и pull request.

## Структура проекта

```
morse-project/
├── backend/            # основной сервис (кодирование/декодирование)
│   ├── app/
│   │   ├── main.py     # эндпоинты FastAPI
│   │   ├── morse.py    # таблица Морзе и функции encode/decode
│   │   └── schemas.py  # pydantic-модели
│   └── tests/          # pytest: morse + API
├── stats-service/      # статистика (SQLite)
│   ├── main.py
│   └── tests/
├── export-service/     # экспорт TXT/CSV/PDF
│   ├── main.py
│   └── tests/
├── frontend/           # nginx + статика (index.html, app.js, style.css)
├── docker-compose.yml
└── .github/workflows/  # CI
```
