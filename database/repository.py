import os
import json
import logging
import pandas as pd
from sqlalchemy import text
from .models import orders_table, athletes_table, students_table
from .connection import get_db_engine, is_postgres_connected, init_db

logger = logging.getLogger(__name__)

def load_data_from_db_or_json(json_file_path: str):
    """
    Loads athletes, orders, and students.
    If PostgreSQL is connected, loads from DB (and auto-seeds from json if DB is empty).
    Otherwise loads from json_file_path.
    Returns: (df_athletes, df_orders, df_students, is_postgres_active)
    """
    engine = get_db_engine()
    if engine and is_postgres_connected():
        init_db(engine)
        try:
            with engine.connect() as conn:
                ath_count = conn.execute(text("SELECT count(*) FROM athletes")).scalar()
                # If table is empty, auto-seed from json
                if (ath_count is None or ath_count == 0) and os.path.exists(json_file_path):
                    migrate_json_to_db(json_file_path, engine)
                
                df_ath = pd.read_sql("SELECT * FROM athletes ORDER BY id DESC", conn)
                df_ord = pd.read_sql("SELECT * FROM orders ORDER BY id DESC", conn)
                df_stu = pd.read_sql("SELECT * FROM students ORDER BY id ASC", conn)
                
                # Parse JSON ranks for students if stored as string
                if not df_stu.empty and "ranks" in df_stu.columns:
                    def parse_ranks(val):
                        if isinstance(val, list):
                            return val
                        if isinstance(val, str):
                            try:
                                return json.loads(val)
                            except:
                                return [val] if val else []
                        return []
                    df_stu["ranks"] = df_stu["ranks"].apply(parse_ranks)
                    
                return df_ath, df_ord, df_stu, True
        except Exception as e:
            logger.error(f"Failed loading from DB, falling back to JSON: {e}")

    # Fallback to JSON
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df_ath = pd.DataFrame(data["athletes"])
        df_ord = pd.DataFrame(data["orders"])
        df_stu = pd.DataFrame(data.get("students", []))
        return df_ath, df_ord, df_stu, False
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), False

def migrate_json_to_db(json_file_path: str, engine=None):
    """Migrates records from JSON file into PostgreSQL tables."""
    if engine is None:
        engine = get_db_engine()
    if engine is None or not os.path.exists(json_file_path):
        return False
    init_db(engine)
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with engine.begin() as conn:
        c = conn.execute(text("SELECT count(*) FROM athletes")).scalar()
        if c and c > 0:
            return True # already migrated
            
        for o in data.get("orders", []):
            conn.execute(
                orders_table.insert().values(
                    org=o.get("org", ""),
                    num=o.get("num", ""),
                    date=o.get("date", ""),
                    city=o.get("city", ""),
                    subj=o.get("subj", ""),
                    count=o.get("count", 0),
                    file=o.get("file", "")
                )
            )
            
        for a in data.get("athletes", []):
            by = a.get("birth_year")
            try:
                by = int(by) if by else None
            except:
                by = None
            conn.execute(
                athletes_table.insert().values(
                    fio=a.get("fio", ""),
                    birth_year=by,
                    birth_date=str(a.get("birth_date", "")),
                    rank=a.get("rank", ""),
                    rank_type=a.get("rank_type", ""),
                    order_num=a.get("order_num", ""),
                    order_date=a.get("order_date", ""),
                    org=a.get("org", ""),
                    city=a.get("city", ""),
                    competition=a.get("competition", ""),
                    discipline=a.get("discipline", ""),
                    place=a.get("place", ""),
                    club=a.get("club", ""),
                    notes=a.get("notes", ""),
                    student_branch=a.get("student_branch", ""),
                    student_contract=a.get("student_contract", "")
                )
            )
            
        for s in data.get("students", []):
            by = s.get("birth_year")
            try:
                by = int(by) if by else None
            except:
                by = None
            ranks_json = json.dumps(s.get("ranks", []), ensure_ascii=False)
            conn.execute(
                students_table.insert().values(
                    fio=s.get("fio", ""),
                    fam=s.get("fam", ""),
                    imya=s.get("imya", ""),
                    otch=s.get("otch", ""),
                    birth_year=by,
                    birth_date=str(s.get("birth_date", "")),
                    branch=s.get("branch", ""),
                    contract=s.get("contract", ""),
                    notes=s.get("notes", ""),
                    has_rank=bool(s.get("has_rank", False)),
                    ranks=ranks_json
                )
            )
    return True

def save_order_and_athletes_to_postgres(order_dict: dict, athletes_list: list, engine=None):
    """Saves a new order and list of athletes into PostgreSQL tables and updates students."""
    if engine is None:
        engine = get_db_engine()
    if engine is None or not is_postgres_connected():
        return False
        
    try:
        with engine.begin() as conn:
            # Insert order
            conn.execute(
                orders_table.insert().values(
                    org=order_dict.get("org", ""),
                    num=order_dict.get("num", ""),
                    date=order_dict.get("date", ""),
                    city=order_dict.get("city", ""),
                    subj=order_dict.get("subj", ""),
                    count=order_dict.get("count", 0),
                    file=order_dict.get("file", "")
                )
            )
            
            # Insert athletes & update students
            for a in athletes_list:
                by = a.get("birth_year")
                try:
                    by = int(by) if by else None
                except:
                    by = None
                conn.execute(
                    athletes_table.insert().values(
                        fio=a.get("fio", ""),
                        birth_year=by,
                        birth_date=str(a.get("birth_date", "")),
                        rank=a.get("rank", ""),
                        rank_type=a.get("rank_type", ""),
                        order_num=a.get("order_num", ""),
                        order_date=a.get("order_date", ""),
                        org=a.get("org", ""),
                        city=a.get("city", ""),
                        competition=a.get("competition", ""),
                        discipline=a.get("discipline", ""),
                        place=a.get("place", ""),
                        club=a.get("club", ""),
                        notes=a.get("notes", ""),
                        student_branch=a.get("student_branch", ""),
                        student_contract=a.get("student_contract", "")
                    )
                )
                
                # Check student and update
                fio_clean = a.get("fio", "").strip()
                if fio_clean:
                    st_row = conn.execute(
                        text("SELECT id, ranks FROM students WHERE lower(fio) = lower(:fio)"),
                        {"fio": fio_clean}
                    ).fetchone()
                    if st_row:
                        st_id, cur_ranks_raw = st_row
                        try:
                            cur_ranks = json.loads(cur_ranks_raw) if cur_ranks_raw else []
                        except:
                            cur_ranks = []
                        if a.get("rank") and a["rank"] not in cur_ranks:
                            cur_ranks.append(a["rank"])
                        conn.execute(
                            text("UPDATE students SET has_rank = TRUE, ranks = :rnk WHERE id = :id"),
                            {"rnk": json.dumps(cur_ranks, ensure_ascii=False), "id": st_id}
                        )
        return True
    except Exception as e:
        logger.error(f"Failed to save to PostgreSQL: {e}")
        return False
