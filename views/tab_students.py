import streamlit as st
import pandas as pd
from config import ALL_STUDENT_COLS

def render_students_tab(df_students: pd.DataFrame):
    """Renders Tab 2: База обучающихся Академии пилотов «АтмоС»."""
    st.markdown("#### База обучающихся Академии пилотов «АтмоС»")
    
    if df_students.empty:
        st.info("Данные по ученикам не найдены.")
        return

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
    
    def set_student_cols(cols):
        st.session_state["selected_student_cols"] = cols

    if "selected_student_cols" not in st.session_state:
        st.session_state["selected_student_cols"] = list(ALL_STUDENT_COLS.keys())

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
