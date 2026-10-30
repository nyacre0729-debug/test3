#!/usr/bin/env bash
# Полный цикл: БД -> сбор данных -> анализ -> графики
set -e

echo "==> Запуск PostgreSQL"
docker compose up -d db
sleep 3

echo "==> Сбор данных (скачивание выгрузки trudvsem.ru, ~1,9 ГБ)"
python get_data.py

echo "==> Анализ и визуализация"
python analyze.py

echo "==> Готово. Результаты: figures/, results/"
