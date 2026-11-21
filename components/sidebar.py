import os
import streamlit as st
import pandas as pd
from config import (
    ALL_MAIN_COLS,
    XLSX_FILE,
    CSV_FILE,
    MD_FILE
)

def set_main_cols(cols):
    st.session_state["selected_main_cols"] = cols

def render_sidebar(df_athletes: pd.DataFrame):
    """
    Renders sidebar column presets, multiselect, filters, and export buttons.
    Returns: (filtered_df, active_cols)
    """
    if "selected_main_cols" not in st.session_state:
        st.session_state["selected_main_cols"] = list(ALL_MAIN_COLS.keys())

    # 1. Column Picker
    st.sidebar.markdown("### 🎛️ Столбцы сводного реестра")
    p1, p2, p3 = st.sidebar.columns(3)
    p1.button("Все", key="sb_btn_all", on_click=set_main_cols, args=(list(ALL_MAIN_COLS.keys()),), help="Показать все 12 столбцов")
    p2.button("Кратко", key="sb_btn_brief", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "№ приказа", "Дата приказа", "Город"],), help="Краткий вид: ФИО, Разряд, № приказа, Дата, Город")
    p3.button("Спорт", key="sb_btn_sport", on_click=set_main_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "Категория", "№ приказа", "Дисциплина", "Результат / Статус"],), help="Спортивные квалификации и результаты")

    selected_main_cols = st.sidebar.multiselect(
        "Удаляйте крестиком ✕ или добавляйте:",
        options=list(ALL_MAIN_COLS.keys()),
        key="selected_main_cols"
    )

    # 2. Filters
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

    # 3. Downloads
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
                label="📄 Выгрузить в CSV (.csv)",
                data=f,
                file_name="Реестр_приказов_и_разрядов.csv",
                mime="text/csv",
                width='stretch'
            )

    if os.path.exists(MD_FILE):
        with open(MD_FILE, "rb") as f:
            st.sidebar.download_button(
                label="📝 Выгрузить в Markdown (.md)",
                data=f,
                file_name="Реестр_приказов_и_разрядов.md",
                mime="text/markdown",
                width='stretch'
            )

    return filtered_df, selected_main_cols
