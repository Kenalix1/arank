"""
Backward-compatibility facade for database package.
All implementations are organized in the `database/` package.
"""

from database import (
    get_database_url,
    get_db_engine,
    is_postgres_connected,
    init_db,
    orders_table,
    athletes_table,
    students_table,
    metadata,
    load_data_from_db_or_json,
    migrate_json_to_db,
    save_order_and_athletes_to_postgres,
    save_registry_files
)

__all__ = [
    "get_database_url",
    "get_db_engine",
    "is_postgres_connected",
    "init_db",
    "orders_table",
    "athletes_table",
    "students_table",
    "metadata",
    "load_data_from_db_or_json",
    "migrate_json_to_db",
    "save_order_and_athletes_to_postgres",
    "save_registry_files"
]
