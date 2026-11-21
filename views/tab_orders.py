import os
import streamlit as st
import pandas as pd
from config import BASE_DIR, PHOTOS_DIR, ALL_ORDER_COLS

def render_orders_tab(df_orders: pd.DataFrame, df_athletes: pd.DataFrame):
    """Renders Tab 3: Приказы и фото документов."""
    if df_orders.empty:
        st.info("Приказы не найдены.")
        return

    if "selected_order_cols" not in st.session_state:
        st.session_state["selected_order_cols"] = list(ALL_ORDER_COLS.keys())

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
        # Full width photo mode
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
