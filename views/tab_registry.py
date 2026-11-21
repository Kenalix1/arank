import streamlit as st
import pandas as pd
from config import ALL_MAIN_COLS, MAIN_COL_MAP

def render_registry_tab(filtered_df: pd.DataFrame, selected_main_cols: list, total_count: int):
    """Renders Tab 1: Main Registry Table with presets and column configurator."""
    display_df = filtered_df.copy()
    display_df["birth"] = display_df.apply(
        lambda row: str(row["birth_date"]) if row.get("birth_date") else (str(int(row["birth_year"])) if row.get("birth_year") else "-"),
        axis=1
    )

    table_df = display_df[[c for c in MAIN_COL_MAP.keys() if c in display_df.columns]].rename(columns=MAIN_COL_MAP)
    active_cols = [c for c in selected_main_cols if c in table_df.columns]

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"#### Записи реестра (отобрано: **{len(filtered_df)}** из {total_count})")
    with col_t2:
        st.markdown(
            f"<div style='text-align: right; color: #94A3B8; font-size: 0.9rem; padding-top: 6px;'>"
            f"Столбцов: <b style='color: #60A5FA;'>{len(active_cols)}</b> из {len(ALL_MAIN_COLS)}</div>",
            unsafe_allow_html=True
        )

    def set_cols(cols):
        st.session_state["selected_main_cols"] = cols

    with st.expander("⚙️ Настроить столбцы реестра (быстрые наборы и переключатели)", expanded=False):
        tb1, tb2, tb3, tb4 = st.columns(4)
        tb1.button("Показать все (12)", key="t_btn_all", on_click=set_cols, args=(list(ALL_MAIN_COLS.keys()),))
        tb2.button("Краткий вид (5)", key="t_btn_brief", on_click=set_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "№ приказа", "Дата приказа", "Город"],))
        tb3.button("Спорт и соревнования", key="t_btn_sport", on_click=set_cols, args=(["ФИО спортсмена / ученика", "Разряд / Статус", "Категория", "№ приказа", "Дисциплина", "Результат / Статус"],))
        tb4.button("Академия АтмоС", key="t_btn_acad", on_click=set_cols, args=(["ФИО спортсмена / ученика", "Дата / Год", "Разряд / Статус", "Филиал / Клуб", "Примечания / Договор"],))
        st.caption("💡 Вы также можете удалять столбцы крестиком `✕` или добавлять их в левой боковой панели под блоком **«🎛️ Столбцы сводного реестра»**.")

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
                "Дисциплина": st.column_config.TextColumn(width="medium"),
                "Результат / Статус": st.column_config.TextColumn(width="medium"),
            }
        )
    else:
        st.warning("⚠️ Все столбцы скрыты. Выберите нужные столбцы в меню настройки выше или в левой панели.")
