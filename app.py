import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="АтмоС Арена | Реестр разрядов и учеников",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Dark Theme Background */
    .stApp {
        background-color: #090D16 !important;
        color: #F1F5F9;
    }

    /* Hero Banner Dark Glassmorphism */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #131C31 40%, #1E1B4B 100%);
        border-radius: 20px;
        padding: 32px 36px;
        color: #FFFFFF;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6), 0 0 25px rgba(59, 130, 246, 0.1);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(30, 58, 138, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(96, 165, 250, 0.3);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #60A5FA;
        margin-bottom: 12px;
    }
    
    .hero-title {
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 8px;
        background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        max-width: 680px;
        line-height: 1.55;
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #10B981;
    }

    /* KPI Cards Dark */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        background: #111827;
        border-radius: 16px;
        padding: 18px 16px;
        border: 1px solid #1F2937;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #374151;
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.4);
    }
    
    .kpi-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        margin-bottom: 12px;
    }
    
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .kpi-num {
        font-size: 1.65rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
    }

    /* Dark Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #111827 !important;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #1F2937 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #94A3B8 !important;
        padding: 0 16px;
        transition: all 0.15s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #60A5FA !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }

    /* Dark Profile Card */
    .profile-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .avatar-circle {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        font-weight: 700;
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .rank-pill {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    
    .rank-pill-sport {
        background: rgba(99, 102, 241, 0.2);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    .rank-pill-junior {
        background: rgba(245, 158, 11, 0.2);
        color: #FCD34D;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    .rank-pill-none {
        background: rgba(148, 163, 184, 0.12);
        color: #94A3B8;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    
    /* Timeline item Dark */
    .timeline-item {
        border-left: 2px solid #3B82F6;
        padding-left: 20px;
        margin-left: 8px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -7px;
        top: 2px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #3B82F6;
        border: 2px solid #090D16;
        box-shadow: 0 0 8px #3B82F6;
    }

    /* Dark Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Container borders dark */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 14px !important;
    }

    /* Metric values dark */
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "Реестр_приказов_и_разрядов.json")
XLSX_FILE = os.path.join(BASE_DIR, "Реестр_приказов_и_разрядов.xlsx")
CSV_FILE = os.path.join(BASE_DIR, "Реестр_приказов_и_разрядов.csv")
MD_FILE = os.path.join(BASE_DIR, "Реестр_приказов_и_разрядов.md")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

# Load Data
@st.cache_data
def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        df_ath = pd.DataFrame(data["athletes"])
        df_ord = pd.DataFrame(data["orders"])
        df_stu = pd.DataFrame(data.get("students", []))
        return df_ath, df_ord, df_stu
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_athletes, df_orders, df_students = load_data()

if df_athletes.empty:
    st.error("Файл данных не найден. Убедитесь, что 'Реестр_приказов_и_разрядов.json' находится в папке приложения.")
    st.stop()

# Helper for initials
def get_initials(fio):
    parts = fio.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "АТ"

# Callbacks for column state management (run before widgets are instantiated)
def set_main_cols(cols):
    st.session_state["selected_main_cols"] = cols

def set_student_cols(cols):
    st.session_state["selected_student_cols"] = cols

def set_order_cols(cols):
    st.session_state["selected_order_cols"] = cols

# HERO BANNER DARK
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">
        <span class="pulse-dot"></span>
        АтмоС Арена • Федерация гонок дронов РО
    </div>
    <div class="hero-title">Единый реестр спортсменов и разрядов</div>
    <div class="hero-subtitle">
        Официальные приказы, база обучающихся Академии пилотов «АтмоС», хронология квалификаций и присвоения спортивных разрядов по гонкам дронов (беспилотных воздушных судов).
    </div>
</div>
""", unsafe_allow_html=True)

# TOP KPI STATS DARK
total_entries = len(df_athletes)
unique_people = df_athletes["fio"].nunique()
total_students = len(df_students)
sport_ranks = (df_athletes["rank_type"] == "Спортивный").sum()
junior_ranks = (df_athletes["rank_type"] == "Юношеский").sum()
no_ranks = (df_athletes["rank"] == "Без разряда").sum()

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(37, 99, 235, 0.2); color: #60A5FA;">🗂️</div>
        <div class="kpi-label">Всего записей</div>
        <div class="kpi-num">{total_entries}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.2); color: #34D399;">👥</div>
        <div class="kpi-label">Спортсменов</div>
        <div class="kpi-num">{unique_people}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(147, 51, 234, 0.2); color: #C084FC;">🎓</div>
        <div class="kpi-label">В Академии</div>
        <div class="kpi-num">{total_students}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.2); color: #818CF8;">🏆</div>
        <div class="kpi-label">Спортивные</div>
        <div class="kpi-num">{sport_ranks}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.2); color: #FBBF24;">🎖️</div>
        <div class="kpi-label">Юношеские</div>
        <div class="kpi-num">{junior_ranks}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background: rgba(148, 163, 184, 0.15); color: #94A3B8;">⏳</div>
        <div class="kpi-label">Без разряда</div>
        <div class="kpi-num">{no_ranks}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR: COLUMN PICKER FOR MAIN REGISTRY
st.sidebar.markdown("### 🎛️ Столбцы сводного реестра")

ALL_MAIN_COLS = {
    "ФИО спортсмена / ученика": "fio",
    "Дата / Год": "birth",
    "Разряд / Статус": "rank",
    "Категория": "rank_type",
    "№ приказа": "order_num",
    "Дата приказа": "order_date",
    "Город": "city",
    "Орган / Организация": "org",
    "Дисциплина": "discipline",
    "Результат / Статус": "place",
    "Филиал / Клуб": "club",
    "Примечания / Договор": "notes"
}

if "selected_main_cols" not in st.session_state:
    st.session_state["selected_main_cols"] = list(ALL_MAIN_COLS.keys())

# Quick presets in sidebar
p1, p2, p3 = st.sidebar.columns(3)
p1.button("Все", key="sb_btn_all", on_click=set_main_cols, args=(list(ALL_MAIN_COLS.keys()),), help="Показать все 12 столбцов")
p2.button("Кратко", key="sb_btn_brief", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "№ приказа", "Дата приказа", "Город"],), help="Краткий вид: ФИО, Разряд, № приказа, Дата, Город")
p3.button("Спорт", key="sb_btn_sport", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "Категория", "№ приказа", "Дисциплина", "Результат / Статус"],), help="Спортивные квалификации и результаты")

selected_main_cols = st.sidebar.multiselect(
    "Удаляйте крестиком ✕ или добавляйте:",
    options=list(ALL_MAIN_COLS.keys()),
    key="selected_main_cols"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Фильтрация и поиск")

search_fio = st.sidebar.text_input("Поиск по фамилии или имени:", placeholder="например: Хлыбов, Сазонов...")

category_filter = st.sidebar.radio(
    "Категория учета:",
    options=["Все записи", "Спортивные разряды", "Юношеские разряды", "Только аттестованные", "Ученики без разряда"],
    index=0
)

all_ranks = sorted(df_athletes["rank"].unique().tolist())
selected_ranks = st.sidebar.multiselect(
    "Выбор разряда:",
    options=all_ranks,
    default=[]
)

all_cities = sorted([c for c in df_athletes["city"].dropna().unique().tolist() if c])
selected_cities = st.sidebar.multiselect(
    "Город / Муниципалитет:",
    options=all_cities,
    default=[]
)

# Apply filters
filtered_df = df_athletes.copy()

if search_fio:
    filtered_df = filtered_df[filtered_df["fio"].str.contains(search_fio, case=False, na=False)]

if category_filter == "Спортивные разряды":
    filtered_df = filtered_df[filtered_df["rank_type"] == "Спортивный"]
elif category_filter == "Юношеские разряды":
    filtered_df = filtered_df[filtered_df["rank_type"] == "Юношеский"]
elif category_filter == "Только аттестованные":
    filtered_df = filtered_df[filtered_df["rank"] != "Без разряда"]
elif category_filter == "Ученики без разряда":
    filtered_df = filtered_df[filtered_df["rank"] == "Без разряда"]

if selected_ranks:
    filtered_df = filtered_df[filtered_df["rank"].isin(selected_ranks)]

if selected_cities:
    filtered_df = filtered_df[filtered_df["city"].isin(selected_cities)]

# Downloads in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Экспорт данных")

if os.path.exists(XLSX_FILE):
    with open(XLSX_FILE, "rb") as f:
        st.sidebar.download_button(
            label="📊 Выгрузить в Excel (.xlsx)",
            data=f,
            file_name="Реестр_приказов_и_разрядов.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "rb") as f:
        st.sidebar.download_button(
            label="📄 Скачать CSV (.csv)",
            data=f,
            file_name="Реестр_приказов_и_разрядов.csv",
            mime="text/csv",
            width='stretch'
        )

if os.path.exists(MD_FILE):
    with open(MD_FILE, "rb") as f:
        st.sidebar.download_button(
            label="📝 Документ Markdown (.md)",
            data=f,
            file_name="Реестр_приказов_и_разрядов.md",
            mime="text/markdown",
            width='stretch'
        )

# TABS
tab_table, tab_students, tab_orders, tab_stats, tab_athlete = st.tabs([
    "📋 Сводный реестр",
    "🎓 Ученики Академии АтмоС",
    "📑 Приказы и фото документов",
    "📊 Аналитика",
    "👤 Персональное досье"
])

# TAB 1: MAIN REGISTRY TABLE
with tab_table:
    display_df = filtered_df.copy()
    display_df["birth"] = display_df.apply(
        lambda row: str(row["birth_date"]) if row["birth_date"] else (str(int(row["birth_year"])) if row["birth_year"] else "-"),
        axis=1
    )
    
    col_map = {
        "fio": "ФИО спортсмена / ученика",
        "birth": "Дата / Год",
        "rank": "Разряд / Статус",
        "rank_type": "Категория",
        "order_num": "№ приказа",
        "order_date": "Дата приказа",
        "city": "Город",
        "org": "Орган / Организация",
        "discipline": "Дисциплина",
        "place": "Результат / Статус",
        "club": "Филиал / Клуб",
        "notes": "Примечания / Договор"
    }
    
    table_df = display_df[list(col_map.keys())].rename(columns=col_map)
    active_cols = [c for c in selected_main_cols if c in table_df.columns]
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"#### Записи реестра (отобрано: **{len(filtered_df)}** из {len(df_athletes)})")
    with col_t2:
        st.markdown(f"<div style='text-align: right; color: #94A3B8; font-size: 0.9rem; padding-top: 6px;'>Столбцов: <b style='color: #60A5FA;'>{len(active_cols)}</b> из {len(ALL_MAIN_COLS)}</div>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Настроить столбцы реестра (быстрые наборы и переключатели)", expanded=False):
        tb1, tb2, tb3, tb4 = st.columns(4)
        tb1.button("Показать все (12)", key="t_btn_all", on_click=set_main_cols, args=(list(ALL_MAIN_COLS.keys()),))
        tb2.button("Краткий вид (5)", key="t_btn_brief", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "№ приказа", "Дата приказа", "Город"],))
        tb3.button("Спорт и соревнования", key="t_btn_sport", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "Категория", "№ приказа", "Дисциплина", "Результат / Статус"],))
        tb4.button("Академия АтмоС", key="t_btn_acad", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Дата / Год", "Разряд / Статус", "Филиал / Клуб", "Примечания / Договор"],))
        st.caption("💡 Вы также можете в любой момент удалять столбцы крестиком `✕` или добавлять их в левой боковой панели под блоком **«🎛️ Столбцы сводного реестра»**.")

    if active_cols:
        st.dataframe(
            table_df[active_cols],
            width='stretch',
            hide_index=True,
            height=540,
            column_config={
                "ФИО спортсмена / ученика": st.column_config.TextColumn(width="medium"),
                "Разряд / Статус": st.column_config.TextColumn(width="medium"),
                "Категория": st.column_config.TextColumn(width="small"),
                "№ приказа": st.column_config.TextColumn(width="small"),
                "Дата приказа": st.column_config.TextColumn(width="small"),
                "Город": st.column_config.TextColumn(width="small"),
            }
        )
    else:
        st.warning("⚠️ Все столбцы скрыты. Выберите нужные столбцы в меню настройки выше или в левой панели.")

# TAB 2: STUDENTS BASE
ALL_STUDENT_COLS = {
    "ФИО ученика": "fio",
    "Дата рождения": "birth_date",
    "Филиал / Занятия": "branch",
    "№ Договора": "contract",
    "Статус": "status_label",
    "Присвоенные разряды": "ranks_label",
    "Примечания": "notes"
}

if "selected_student_cols" not in st.session_state:
    st.session_state["selected_student_cols"] = list(ALL_STUDENT_COLS.keys())

with tab_students:
    st.markdown("#### База обучающихся Академии пилотов «АтмоС»")
    
    if not df_students.empty:
        with st.container(border=True):
            fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
            with fcol1:
                search_stu = st.text_input("🔍 Быстрый поиск ученика по ФИО или договору:", key="search_stu")
            with fcol2:
                status_opt = st.selectbox("Статус квалификации:", ["Все ученики", "Только с разрядами", "Без разряда (обучаются)"], key="status_opt")
            with fcol3:
                all_branches = ["Все филиалы"] + sorted(list(set(b for b in df_students["branch"].dropna() if b)))
                branch_opt = st.selectbox("Локация / Филиал:", all_branches, key="branch_opt")
            
        stu_filtered = df_students.copy()
        if search_stu:
            mask = (
                stu_filtered["fio"].str.contains(search_stu, case=False, na=False) | 
                stu_filtered["contract"].str.contains(search_stu, case=False, na=False)
            )
            stu_filtered = stu_filtered[mask]
            
        if status_opt == "Только с разрядами":
            stu_filtered = stu_filtered[stu_filtered["has_rank"] == True]
        elif status_opt == "Без разряда (обучаются)":
            stu_filtered = stu_filtered[stu_filtered["has_rank"] == False]
            
        if branch_opt != "Все филиалы":
            stu_filtered = stu_filtered[stu_filtered["branch"] == branch_opt]
            
        stu_display = stu_filtered.copy()
        stu_display["status_label"] = stu_display["has_rank"].apply(lambda x: "🏆 Аттестован" if x else "⏳ Обучается")
        stu_display["ranks_label"] = stu_display["ranks"].apply(lambda r: ", ".join(r) if r else "-")
        
        s_renames = {
            "fio": "ФИО ученика",
            "birth_date": "Дата рождения",
            "branch": "Филиал / Занятия",
            "contract": "№ Договора",
            "status_label": "Статус",
            "ranks_label": "Присвоенные разряды",
            "notes": "Примечания"
        }
        stu_table_df = stu_display[list(s_renames.keys())].rename(columns=s_renames)
        
        with st.expander("⚙️ Настройка столбцов учеников (скрыть / показать)", expanded=False):
            sb1, sb2, sb3 = st.columns(3)
            sb1.button("Все столбцы учеников", key="stu_btn_all", on_click=set_student_cols, args=(list(ALL_STUDENT_COLS.keys()),))
            sb2.button("Кратко (ФИО + Статус + Разряд)", key="stu_btn_brief", on_click=set_student_cols, args=(["ФИО ученика", "Статус", "Присвоенные разряды"],))
            sb3.button("Контакты и филиал", key="stu_btn_contacts", on_click=set_student_cols, args=(["ФИО ученика", "Дата рождения", "Филиал / Занятия", "№ Договора"],))
                
            selected_student_cols = st.multiselect(
                "Отображаемые столбцы учеников (удаляйте крестиком ✕):",
                options=list(ALL_STUDENT_COLS.keys()),
                key="selected_student_cols"
            )
            
        active_s_cols = [c for c in selected_student_cols if c in stu_table_df.columns]
        if active_s_cols:
            st.dataframe(
                stu_table_df[active_s_cols],
                width='stretch',
                hide_index=True,
                height=500,
                column_config={
                    "ФИО ученика": st.column_config.TextColumn(width="medium"),
                    "Статус": st.column_config.TextColumn(width="medium"),
                    "Присвоенные разряды": st.column_config.TextColumn(width="large")
                }
            )
        else:
            st.warning("⚠️ Все столбцы таблицы учеников скрыты. Выберите столбцы выше.")
    else:
        st.info("Данные по ученикам не найдены.")

# TAB 3: ORDERS & PHOTO PREVIEWS
ALL_ORDER_COLS = {
    "ФИО": "fio",
    "Год": "birth_year",
    "Разряд": "rank",
    "Дисциплина": "discipline",
    "Результат": "place",
    "Примечание": "notes"
}

if "selected_order_cols" not in st.session_state:
    st.session_state["selected_order_cols"] = list(ALL_ORDER_COLS.keys())

with tab_orders:
    col_o_head1, col_o_head2 = st.columns([3, 1])
    with col_o_head1:
        st.markdown("#### Официальные приказы ведомств и федерации")
    with col_o_head2:
        expand_photo = st.toggle("🖼️ Фото на весь экран", value=False, key="toggle_expand_photo")
    
    order_options = []
    for idx, row in df_orders.iterrows():
        order_options.append(f"{row['num']} от {row['date']} • {row['org']} ({row['city']})")
    
    selected_order_idx = st.selectbox(
        "Выберите документ для подробного просмотра:",
        options=range(len(order_options)),
        format_func=lambda i: order_options[i]
    )
    
    cur_order = df_orders.iloc[selected_order_idx]
    
    photo_files = [f.strip() for f in str(cur_order["file"]).split(",")]
    img_path = None
    for pfile in photo_files:
        matches = [f for f in os.listdir(PHOTOS_DIR) if cur_order["num"].replace("№", "").strip() in f or cur_order["date"] in f] if os.path.exists(PHOTOS_DIR) else []
        if matches:
            img_path = os.path.join(PHOTOS_DIR, matches[0])
            break
        elif os.path.exists(os.path.join(BASE_DIR, pfile)):
            img_path = os.path.join(BASE_DIR, pfile)
            break
        elif os.path.exists(os.path.join(PHOTOS_DIR, pfile)):
            img_path = os.path.join(PHOTOS_DIR, pfile)
            break
            
    athletes_in_order = df_athletes[
        (df_athletes["order_num"] == cur_order["num"]) & 
        (df_athletes["order_date"] == cur_order["date"])
    ]
    
    if not expand_photo:
        col_info, col_img = st.columns([1, 1], gap="medium")
        
        with col_info:
            with st.container(border=True):
                st.markdown(f"### {cur_order['num']}")
                st.markdown(f"**Орган власти / Федерация:** {cur_order['org']}")
                st.markdown(f"**Дата приказа:** {cur_order['date']}")
                st.markdown(f"**Город / Район:** {cur_order['city']}")
                st.markdown(f"**Предмет приказа:** {cur_order['subj']}")
                st.markdown(f"**Количество спортсменов:** {cur_order['count']} чел.")
            
            st.markdown("##### 👥 Спортсмены, вошедшие в данный приказ:")
            
            with st.expander("⚙️ Настроить столбцы списка приказа", expanded=False):
                selected_order_cols = st.multiselect(
                    "Столбцы (удаляйте крестиком ✕):",
                    options=list(ALL_ORDER_COLS.keys()),
                    key="selected_order_cols"
                )
            
            sub_table = athletes_in_order[["fio", "birth_year", "rank", "discipline", "place", "notes"]].rename(columns={
                "fio": "ФИО",
                "birth_year": "Год",
                "rank": "Разряд",
                "discipline": "Дисциплина",
                "place": "Результат",
                "notes": "Примечание"
            })
            
            active_o_cols = [c for c in selected_order_cols if c in sub_table.columns]
            if active_o_cols:
                st.dataframe(sub_table[active_o_cols], width='stretch', hide_index=True)
            else:
                st.warning("⚠️ Все столбцы списка скрыты. Выберите столбцы выше.")
            
        with col_img:
            st.markdown("##### 📷 Фотокопия оригинала документа:")
            if img_path and os.path.exists(img_path):
                with st.container(border=True):
                    st.image(img_path, caption=f"Оригинал: {cur_order['num']}", width='stretch')
            else:
                st.info(f"Файл фото: `{cur_order['file']}`.")
    else:
        # Full width photo mode when requested!
        with st.container(border=True):
            ci1, ci2, ci3, ci4 = st.columns(4)
            ci1.metric("Номер приказа", cur_order['num'])
            ci2.metric("Дата", cur_order['date'])
            ci3.metric("Город", cur_order['city'])
            ci4.metric("Спортсменов", f"{cur_order['count']} чел.")
            st.caption(f"**Орган / Федерация:** {cur_order['org']} • **Предмет:** {cur_order['subj']}")
        
        st.markdown("##### 📷 Фотокопия оригинала документа (полноэкранный режим):")
        if img_path and os.path.exists(img_path):
            with st.container(border=True):
                st.image(img_path, caption=f"Оригинал: {cur_order['num']}", width='stretch')
        else:
            st.info(f"Файл фото: `{cur_order['file']}`.")

# TAB 4: ANALYTICS (DARK PLOTLY)
with tab_stats:
    st.markdown("#### Аналитический обзор квалификаций")
    
    col_chart1, col_chart2 = st.columns(2, gap="medium")
    
    with col_chart1:
        with st.container(border=True):
            rank_only = df_athletes[df_athletes["rank"] != "Без разряда"]
            rank_counts = rank_only["rank"].value_counts().reset_index()
            rank_counts.columns = ["Разряд", "Количество"]
            fig1 = px.bar(
                rank_counts,
                x="Разряд",
                y="Количество",
                color="Разряд",
                title="<b>Распределение присвоенных разрядов</b>",
                text="Количество",
                template="plotly_dark",
                color_discrete_sequence=['#3B82F6', '#6366F1', '#F59E0B', '#10B981', '#8B5CF6']
            )
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(t=40, b=20, l=20, r=20),
                font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
            )
            st.plotly_chart(fig1, width='stretch')
        
    with col_chart2:
        with st.container(border=True):
            if not df_students.empty:
                branch_data = df_students["branch"].apply(lambda b: "Аксай" if "аксай" in str(b).lower() else ("Пушкинская" if "пушкинская" in str(b).lower() else "Другое"))
                b_counts = branch_data.value_counts().reset_index()
                b_counts.columns = ["Филиал", "Учеников"]
                fig2 = px.pie(
                    b_counts,
                    names="Филиал",
                    values="Учеников",
                    title="<b>Распределение учеников Академии по филиалам</b>",
                    hole=0.5,
                    template="plotly_dark",
                    color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B']
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=40, b=20, l=20, r=20),
                    font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
                )
                st.plotly_chart(fig2, width='stretch')
            else:
                city_counts = df_athletes["city"].value_counts().reset_index()
                city_counts.columns = ["Город", "Количество"]
                fig2 = px.pie(city_counts, names="Город", values="Количество", title="<b>Распределение по городам</b>", template="plotly_dark")
                st.plotly_chart(fig2, width='stretch')
        
    # Age distribution
    with st.container(border=True):
        valid_years = df_athletes[df_athletes["birth_year"] != ""]["birth_year"].dropna().astype(int)
        valid_years = valid_years[valid_years >= 1975]
        if not valid_years.empty:
            year_counts = valid_years.value_counts().sort_index().reset_index()
            year_counts.columns = ["Год рождения", "Количество"]
            fig3 = px.bar(
                year_counts,
                x="Год рождения",
                y="Количество",
                title="<b>Возрастной состав: распределение по годам рождения</b>",
                text="Количество",
                template="plotly_dark",
                color_discrete_sequence=['#6366F1']
            )
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=40, b=20, l=20, r=20),
                font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
            )
            st.plotly_chart(fig3, width='stretch')

# TAB 5: ATHLETE / STUDENT DOSSIER
with tab_athlete:
    st.markdown("#### Персональная карточка спортсмена / ученика")
    
    all_names = sorted(df_athletes["fio"].unique().tolist())
    default_idx = all_names.index("Хлыбов Василий Васильевич") if "Хлыбов Василий Васильевич" in all_names else 0
    selected_person = st.selectbox("Выберите пилота из списка:", options=all_names, index=default_idx)
    
    if selected_person:
        records = df_athletes[df_athletes["fio"] == selected_person]
        first_r = records.iloc[0]
        initials = get_initials(selected_person)
        
        ranks_records = records[records["rank"] != "Без разряда"]
        highest_rank = ranks_records.iloc[-1]["rank"] if not ranks_records.empty else "Обучается в Академии"
        pill_class = "rank-pill-sport" if "спортивный" in highest_rank.lower() else ("rank-pill-junior" if "юношеский" in highest_rank.lower() else "rank-pill-none")
        
        # Profile Header Card Dark
        st.markdown(f"""
        <div class="profile-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div class="avatar-circle">{initials}</div>
                <div>
                    <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #F8FAFC;">{selected_person}</h2>
                    <div style="margin-top: 8px;">
                        <span class="rank-pill {pill_class}">🏆 {highest_rank}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Metadata metrics
        m1, m2, m3, m4 = st.columns(4)
        b_val = first_r.get("birth_date") or first_r.get("birth_year") or "Не указана"
        br_val = first_r.get("student_branch") or first_r.get("club") or "АтмоС"
        c_val = first_r.get("student_contract") or "Не указан"
        
        with m1:
            st.metric("Дата / Год рождения", str(b_val))
        with m2:
            st.metric("Локация / Филиал", str(br_val))
        with m3:
            st.metric("Номер договора", str(c_val))
        with m4:
            st.metric("Всего присвоений", len(ranks_records))
            
        st.write("")
        
        # History
        if not ranks_records.empty:
            st.markdown("##### 📜 Хронология присвоения спортивных разрядов:")
            for idx, r in ranks_records.iterrows():
                place_str = f" ({r['place']})" if r['place'] else ""
                notes_str = f" • *{r['notes']}*" if r['notes'] else ""
                club_str = f" • {r['club']}" if r['club'] else ""
                
                st.markdown(f"""
                <div class="timeline-item">
                    <div style="font-size: 0.82rem; font-weight: 600; color: #94A3B8;">{r['order_date']}</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F1F5F9; margin-top: 2px;">
                        {r['rank']} <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">({r['rank_type']})</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #CBD5E1; margin-top: 4px;">
                        📄 <b>Приказ:</b> {r['order_num']} от {r['order_date']} ({r['org']}, {r['city']})
                    </div>
                    <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 2px;">
                        🎯 <b>Дисциплина / Результат:</b> {r['discipline']}{place_str}{club_str}{notes_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.container(border=True):
                st.info("ℹ️ У данного ученика пока нет присвоенных официальных спортивных разрядов. Он проходит программу подготовки в Академии пилотов.")
