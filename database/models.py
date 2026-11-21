from datetime import datetime
from sqlalchemy import (
    Table, Column, Integer, String, Text, Boolean, TIMESTAMP, MetaData
)

metadata = MetaData()

orders_table = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("org", String(255)),
    Column("num", String(100)),
    Column("date", String(50)),
    Column("city", String(100)),
    Column("subj", Text),
    Column("count", Integer),
    Column("file", String(255)),
    Column("created_at", TIMESTAMP, default=datetime.now)
)

athletes_table = Table(
    "athletes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("fio", String(255), index=True),
    Column("birth_year", Integer, nullable=True),
    Column("birth_date", String(50), nullable=True),
    Column("rank", String(100)),
    Column("rank_type", String(50)),
    Column("order_num", String(100)),
    Column("order_date", String(50)),
    Column("org", String(255)),
    Column("city", String(100)),
    Column("competition", Text),
    Column("discipline", String(255)),
    Column("place", String(255)),
    Column("club", String(255)),
    Column("notes", Text),
    Column("student_branch", String(255)),
    Column("student_contract", String(100)),
    Column("created_at", TIMESTAMP, default=datetime.now)
)

students_table = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("fio", String(255), index=True),
    Column("fam", String(100)),
    Column("imya", String(100)),
    Column("otch", String(100)),
    Column("birth_year", Integer, nullable=True),
    Column("birth_date", String(50), nullable=True),
    Column("branch", String(255)),
    Column("contract", String(100)),
    Column("notes", Text),
    Column("has_rank", Boolean, default=False),
    Column("ranks", Text),  # JSON-encoded string for cross-database compatibility
    Column("created_at", TIMESTAMP, default=datetime.now)
)
