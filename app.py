import streamlit as st
import pandas as pd

from config import PAGE_TITLE, PAGE_ICON, JSON_FILE
from styles import inject_custom_css
from database import load_data_from_db_or_json
from components import (
    render_hero_banner,
    render_kpi_metrics,
    render_sidebar,
)
from views import (
    render_registry_tab,
    render_students_tab,
    render_orders_tab,
    render_analytics_tab,
    render_dossier_tab,
    render_upload_tab,
)

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global dark glassmorphism styling
inject_custom_css()

# Data Loading with caching
@st.cache_data(show_spinner=False)
def load_data():
    return load_data_from_db_or_json(JSON_FILE)

df_athletes, df_orders, df_students, is_postgres_active = load_data()

if df_athletes.empty:
    st.error("Ошибка загрузки данных: реестр пуст или файл поврежден.")
    st.stop()

# Header & KPIs
render_hero_banner()
render_kpi_metrics(df_athletes, df_students)

# Sidebar (Filters & Exports)
filtered_df, selected_main_cols = render_sidebar(df_athletes)

# Main Navigation Tabs
tab_table, tab_students, tab_orders, tab_stats, tab_athlete, tab_upload = st.tabs([
    "📋 Сводный реестр",
    "🎓 Ученики Академии АтмоС",
    "📑 Приказы и фото документов",
    "📊 Аналитика",
    "👤 Персональное досье",
    "📥 Внесение разрядов"
])

with tab_table:
    render_registry_tab(filtered_df, selected_main_cols, len(df_athletes))

with tab_students:
    render_students_tab(df_students)

with tab_orders:
    render_orders_tab(df_orders, df_athletes)

with tab_stats:
    render_analytics_tab(df_athletes, df_students)

with tab_athlete:
    render_dossier_tab(df_athletes)

with tab_upload:
    render_upload_tab(df_students, is_postgres_active)
