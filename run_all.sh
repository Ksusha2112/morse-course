#!/usr/bin/env bash
# Запуск всех сервисов (Linux/macOS, без Docker). Остановка: Ctrl+C.
set -e
cd "$(dirname "$0")"

(cd stats-service && python -m uvicorn main:app --port 8003) &
P1=$!
(cd export-service && python -m uvicorn main:app --port 8004) &
P2=$!
(cd backend && python -m uvicorn app.main:app --reload --port 8000) &
P3=$!

trap 'kill $P1 $P2 $P3 2>/dev/null' EXIT
echo "Сервисы запущены: http://127.0.0.1:8000/docs (остановка: Ctrl+C)"
wait
