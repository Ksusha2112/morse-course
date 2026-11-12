@echo off
rem Запуск всех сервисов в отдельных окнах (Windows, без Docker)
start "stats-service :8003" cmd /k "cd /d %~dp0stats-service && python -m uvicorn main:app --port 8003"
start "export-service :8004" cmd /k "cd /d %~dp0export-service && python -m uvicorn main:app --port 8004"
start "backend :8000" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"
start http://127.0.0.1:8000/docs
echo Сервисы запущены в отдельных окнах. Закрой окна или нажми Ctrl+C в каждом для остановки.
pause
