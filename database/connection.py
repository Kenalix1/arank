import os
import logging
from sqlalchemy import create_engine, text
from .models import metadata

logger = logging.getLogger(__name__)

def get_database_url():
    """Returns PostgreSQL connection string if configured in env or Streamlit secrets, else None."""
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "DATABASE_URL" in st.secrets:
                u = st.secrets["DATABASE_URL"]
                if u.startswith("postgres://"):
                    u = u.replace("postgres://", "postgresql://", 1)
                return u
            if "postgres" in st.secrets:
                pg = st.secrets["postgres"]
                if isinstance(pg, dict) and "url" in pg:
                    u = pg["url"]
                    if u.startswith("postgres://"):
                        u = u.replace("postgres://", "postgresql://", 1)
                    return u
                elif isinstance(pg, str):
                    if pg.startswith("postgres://"):
                        pg = pg.replace("postgres://", "postgresql://", 1)
                    return pg
    except Exception:
        pass
    return None

_engine = None

def get_db_engine():
    """Returns cached SQLAlchemy engine instance or creates a new one."""
    global _engine
    if _engine is not None:
        return _engine
    db_url = get_database_url()
    if not db_url:
        return None
    try:
        _engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=300)
        return _engine
    except Exception as e:
        logger.warning(f"Could not initialize DB engine for {db_url}: {e}")
        return None

def is_postgres_connected():
    """Checks whether connection to PostgreSQL is currently alive and accessible."""
    engine = get_db_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"PostgreSQL connection test failed: {e}")
        return False

def init_db(engine=None):
    """Initializes tables in database if they do not exist."""
    if engine is None:
        engine = get_db_engine()
    if engine is None:
        return False
    try:
        metadata.create_all(engine)
        return True
    except Exception as e:
        logger.error(f"Error creating DB tables: {e}")
        return False
