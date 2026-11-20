#!/usr/bin/env python3
"""
Скрипт миграции данных из JSON в PostgreSQL.
Использование:
  python3 migrate_to_postgres.py [DATABASE_URL]
Либо через переменную окружения:
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/atmos_crm python3 migrate_to_postgres.py
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "Реестр_приказов_и_разрядов.json")

if len(sys.argv) > 1:
    os.environ["DATABASE_URL"] = sys.argv[1]

from db import get_db_engine, init_db, migrate_json_to_db, is_postgres_connected

def main():
    print("--- Миграция реестра разрядов в PostgreSQL ---")
    if not os.path.exists(JSON_FILE):
        print(f"Ошибка: Файл {JSON_FILE} не найден.")
        sys.exit(1)

    engine = get_db_engine()
    if not engine or not is_postgres_connected():
        print("Ошибка: Не удалось подключиться к PostgreSQL.")
        print("Убедитесь, что PostgreSQL запущен и задана переменная DATABASE_URL.")
        print("Пример: export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/atmos_crm'")
        sys.exit(1)

    print("Подключение к PostgreSQL успешно установлено!")
    print("Создание таблиц (orders, athletes, students)...")
    init_db(engine)

    print(f"Загрузка данных из {JSON_FILE}...")
    success = migrate_json_to_db(JSON_FILE, engine)
    if success:
        print("✅ Миграция успешно завершена! Все данные перенесены в PostgreSQL.")
    else:
        print("❌ Ошибка при миграции данных.")

if __name__ == "__main__":
    main()
