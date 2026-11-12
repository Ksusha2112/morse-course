"""
Запуск всех микросервисов одной командой (без Docker).

    python run_dev.py

Поднимает:
  - stats-service  -> http://localhost:8003
  - export-service -> http://localhost:8004
  - backend        -> http://localhost:8000
и открывает Swagger UI бэкенда в браузере.

Остановка: Ctrl+C (все процессы завершатся вместе со скриптом).
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SERVICES = [
    ("stats-service", 8003),
    ("export-service", 8004),
    ("backend", 8000),
]


def start_services() -> list:
    processes = []
    for folder, port in SERVICES:
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app"
            if folder != "backend" else "app.main:app",
            "--host", "127.0.0.1",
            "--port", str(port),
        ]
        proc = subprocess.Popen(cmd, cwd=BASE_DIR / folder)
        processes.append(proc)
        print(f"[OK] {folder} запущен на http://127.0.0.1:{port}")
    return processes


def wait_ready(timeout: float = 15.0) -> None:
    import urllib.request

    deadline = time.time() + timeout
    for _, port in SERVICES:
        url = f"http://127.0.0.1:{port}/health"
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=1) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                time.sleep(0.3)
        else:
            print(f"[!] {url} не ответил за {timeout:.0f} c (возможно, порт занят)")


def main() -> None:
    print("Запуск микросервисов Азбуки Морзе...\n")
    processes = start_services()
    wait_ready()

    print("\nВсе сервисы готовы:")
    print("  Веб-API (Swagger):  http://127.0.0.1:8000/docs")
    print("  Статистика:         http://127.0.0.1:8003/docs")
    print("  Экспорт:            http://127.0.0.1:8004/docs")
    print("\nОстановка: Ctrl+C\n")

    webbrowser.open("http://127.0.0.1:8000/docs")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nОстанавливаю сервисы...")
        for proc in processes:
            proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("Все сервисы остановлены.")


if __name__ == "__main__":
    main()
