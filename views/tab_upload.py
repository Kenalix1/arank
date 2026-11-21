import os
import json
import streamlit as st
import pandas as pd
from config import BASE_DIR, PHOTOS_DIR, JSON_FILE, KNOWN_RANKS
from database import save_order_and_athletes_to_postgres, save_registry_files

def render_upload_tab(df_students: pd.DataFrame, is_postgres_active: bool):
    """Renders Tab 6: Внесение официального приказа и присвоения разрядов."""
    st.markdown("#### 📥 Внесение официального приказа и присвоения разрядов")
    st.caption("Заполните реквизиты приказа, прикрепите скан или фото документа и укажите спортсменов. Данные сохраняются в базу данных.")
    
    # 1. ORDER METADATA
    with st.container(border=True):
        st.markdown("##### 1️⃣ Реквизиты приказа / документа")
        col_u1, col_u2, col_u3 = st.columns([1, 1, 1])
        with col_u1:
            in_order_num = st.text_input("Номер приказа *", placeholder="например: № 16-ФГДРО или № 125-ПСР", key="in_order_num")
        with col_u2:
            in_order_date = st.date_input("Дата приказа *", format="DD.MM.YYYY", key="in_order_date")
        with col_u3:
            city_suggestions = ["г. Ростов-на-Дону", "г. Батайск", "г. Азов", "г. Новочеркасск", "Аксайский район", "г. Таганрог", "г. Шахты"]
            in_city = st.selectbox("Город / Муниципалитет *", options=city_suggestions + ["Другой (ввести вручную)"], key="in_city")
            if in_city == "Другой (ввести вручную)":
                in_city = st.text_input("Введите город / район:", value="г. Ростов-на-Дону", key="in_city_custom")
                
        col_u4, col_u5 = st.columns([1, 1])
        with col_u4:
            org_suggestions = [
                "РФСОО «Федерация гонок дронов Ростовской области»",
                "УФКС г. Ростова-на-Дону",
                "Отдел по ФКСиТ Администрации Аксайского района",
                "Отдел по ФК и спорту Администрации г. Азова",
                "УФКС Администрации г. Новочеркасска",
                "ДОСААФ"
            ]
            in_org = st.selectbox("Орган власти / Федерация *", options=org_suggestions + ["Другая организация (ввести вручную)"], key="in_org")
            if in_org == "Другая организация (ввести вручную)":
                in_org = st.text_input("Введите наименование органа / федерации:", key="in_org_custom")
        with col_u5:
            in_subj = st.text_input("Предмет приказа / основание", value="Присвоение спортивных / юношеских разрядов по гонкам дронов", key="in_subj")
            
        col_u6, col_u7 = st.columns([1, 1])
        with col_u6:
            disc_suggestions = ["Гонки дронов", "Гонки дронов (класс 75 мм)", "Гонки дронов (класс 200 мм)", "Технический симулятор — гонки БВС"]
            in_disc = st.selectbox("Дисциплина (по умолчанию для всех)", options=disc_suggestions + ["Другая"], key="in_disc")
            if in_disc == "Другая":
                in_disc = st.text_input("Введите дисциплину:", value="Гонки дронов", key="in_disc_custom")
        with col_u7:
            in_base_place = st.text_input("Основание / результат (по умолчанию)", value="Выполнение нормы ЕВСК", key="in_base_place")

    # 2. SCAN / PHOTO UPLOAD
    with st.container(border=True):
        st.markdown("##### 2️⃣ Фотокопия или скриншот документа")
        uploaded_doc = st.file_uploader(
            "Загрузите фотокопию или скриншот приказа (JPG, PNG, PDF):",
            type=["jpg", "jpeg", "png", "webp", "pdf"],
            help="Файл будет сохранен в каталог photos/ и привязан к приказу.",
            key="uploaded_doc"
        )
        if uploaded_doc is not None:
            col_preview1, col_preview2 = st.columns([1, 2])
            with col_preview1:
                if uploaded_doc.type.startswith("image/"):
                    st.image(uploaded_doc, caption=f"Предпросмотр: {uploaded_doc.name}", width='stretch')
                else:
                    st.info(f"📄 Загружен документ: **{uploaded_doc.name}** ({round(uploaded_doc.size / 1024, 1)} КБ)")
            with col_preview2:
                st.success(f"Файл готов к сохранению. Будет прикреплен к приказу {in_order_num or 'б/н'}.")

    # 3. ATHLETES LIST (TEXT PARSER & DATA EDITOR)
    with st.container(border=True):
        st.markdown("##### 3️⃣ Список спортсменов и присваиваемых разрядов")
        st.caption("Вы можете быстро вставить список текстом или отредактировать таблицу ниже. При совпадении с базой учеников дата рождения, филиал и договор подтянутся автоматически.")
        
        tab_input_text, tab_input_table = st.tabs(["📝 Быстрый ввод текстом списком", "📊 Таблица спортсменов"])
        
        if "order_athletes_list" not in st.session_state:
            st.session_state["order_athletes_list"] = [
                {"ФИО": "", "Разряд": "1 юношеский разряд", "Дата рождения": "", "Филиал": "", "Договор": "", "Примечания": ""}
            ]
            
        with tab_input_text:
            text_placeholder = (
                "# Вставьте список спортсменов по одной строке.\n"
                "# Формат строки: ФИО | Разряд | Дата или Год рождения (необязательно)\n"
                "# Примеры:\n"
                "Аристархова Эвелина Игоревна | 3 спортивный разряд\n"
                "Изюмов Кирилл Андреевич | 3 спортивный разряд\n"
                "Моргунова Мария Александровна | 1 юношеский разряд | 16.03.2015\n"
            )
            raw_text = st.text_area("Вставьте текст со списком:", height=150, placeholder=text_placeholder, key="raw_athletes_text")
            if st.button("📋 Разобрать список и заполнить в таблицу", key="btn_parse_text"):
                if raw_text.strip():
                    parsed_rows = []
                    stu_lookup = {}
                    if not df_students.empty:
                        for _, s_row in df_students.iterrows():
                            clean_f = " ".join(str(s_row["fio"]).strip().split()).lower()
                            stu_lookup[clean_f] = s_row
                            
                    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip() and not line.strip().startswith("#")]
                    for line in lines:
                        parts = [p.strip() for p in line.replace(";", "|").replace("\t", "|").split("|")]
                        fio_val = parts[0] if len(parts) > 0 else ""
                        rank_val = parts[1] if len(parts) > 1 else "1 юношеский разряд"
                        birth_val = parts[2] if len(parts) > 2 else ""
                        
                        branch_val = ""
                        contract_val = ""
                        
                        lookup_key = " ".join(fio_val.split()).lower()
                        if lookup_key in stu_lookup:
                            matched_s = stu_lookup[lookup_key]
                            if not birth_val:
                                birth_val = str(matched_s.get("birth_date") or matched_s.get("birth_year") or "")
                            branch_val = str(matched_s.get("branch") or "")
                            contract_val = str(matched_s.get("contract") or "")
                            
                        parsed_rows.append({
                            "ФИО": fio_val,
                            "Разряд": rank_val,
                            "Дата рождения": birth_val,
                            "Филиал": branch_val,
                            "Договор": contract_val,
                            "Примечания": ""
                        })
                    if parsed_rows:
                        st.session_state["order_athletes_list"] = parsed_rows
                        st.success(f"Успешно распознано {len(parsed_rows)} спортсменов! Перейдите на вкладку «Таблица спортсменов» для проверки.")
                        st.rerun()

        with tab_input_table:
            st.caption("Здесь можно отредактировать строки, изменить разряды или добавить новых участников:")
            df_editor_input = pd.DataFrame(st.session_state["order_athletes_list"])
            
            edited_athletes_df = st.data_editor(
                df_editor_input,
                num_rows="dynamic",
                width='stretch',
                column_config={
                    "ФИО": st.column_config.TextColumn("ФИО спортсмена *", width="large", required=True),
                    "Разряд": st.column_config.SelectboxColumn("Присваиваемый разряд *", options=KNOWN_RANKS, required=True, width="medium"),
                    "Дата рождения": st.column_config.TextColumn("Дата / Год рождения", width="medium"),
                    "Филиал": st.column_config.TextColumn("Филиал / Клуб", width="medium"),
                    "Договор": st.column_config.TextColumn("№ Договора", width="small"),
                    "Примечания": st.column_config.TextColumn("Примечание", width="medium"),
                },
                key="editor_athletes"
            )

    # 4. SAVE TO DATABASE
    with st.container(border=True):
        st.markdown("##### 4️⃣ Сохранение в базу данных")
        
        if is_postgres_active:
            st.success("🟢 **База данных PostgreSQL подключена.** Данные сохраняются напрямую в таблицы PostgreSQL.")
        else:
            st.info("ℹ️ **Локальный режим (JSON / Excel / CSV).** Для постоянного подключения к PostgreSQL укажите `DATABASE_URL` в переменных окружения или в настройках `st.secrets`.")
            
        btn_save = st.button("💾 СОХРАНИТЬ ПРИКАЗ И РАЗРЯДЫ В БАЗУ ДАННЫХ", type="primary", width='stretch', key="btn_save_order")
            
        if btn_save:
            if not in_order_num.strip():
                st.error("Пожалуйста, укажите номер приказа (например, № 16-ФГДРО)!")
            else:
                valid_athletes = []
                for _, r in edited_athletes_df.iterrows():
                    fio_str = str(r.get("ФИО", "")).strip()
                    if fio_str and fio_str.lower() != "nan":
                        valid_athletes.append(r)
                        
                if not valid_athletes:
                    st.error("Пожалуйста, добавьте хотя бы одного спортсмена в таблицу!")
                else:
                    with st.spinner("Сохранение приказа и разрядов в базу данных..."):
                        date_str = in_order_date.strftime("%d.%m.%Y")
                        
                        saved_photo_name = "—"
                        if uploaded_doc is not None:
                            ext = os.path.splitext(uploaded_doc.name)[1].lower() or ".jpg"
                            safe_num = "".join(c for c in in_order_num if c.isalnum() or c in "-_").strip()
                            safe_city = in_city.replace("г. ", "").replace(" ", "_")
                            safe_filename = f"Приказ_{safe_num}_{safe_city}_{date_str}{ext}"
                            photo_dest = os.path.join(PHOTOS_DIR, safe_filename)
                            os.makedirs(PHOTOS_DIR, exist_ok=True)
                            with open(photo_dest, "wb") as f_out:
                                f_out.write(uploaded_doc.getbuffer())
                            saved_photo_name = safe_filename
                            
                        # 1. New order entry
                        new_order_entry = {
                            "org": in_org.strip(),
                            "num": in_order_num.strip(),
                            "date": date_str,
                            "city": in_city.strip(),
                            "subj": in_subj.strip(),
                            "count": len(valid_athletes),
                            "file": saved_photo_name
                        }
                        
                        # Load current json for fallback & local exports
                        current_data = {"orders": [], "athletes": [], "students": []}
                        if os.path.exists(JSON_FILE):
                            with open(JSON_FILE, "r", encoding="utf-8") as f_j:
                                current_data = json.load(f_j)
                                
                        current_data["orders"].insert(0, new_order_entry)
                        
                        # 2. Add athletes
                        stu_map = {s["fio"].strip().lower(): s for s in current_data.get("students", [])}
                        
                        new_athletes_entries = []
                        for row_a in valid_athletes:
                            a_fio = str(row_a["ФИО"]).strip()
                            a_rank = str(row_a["Разряд"]).strip()
                            a_bdate = str(row_a.get("Дата рождения", "")).strip()
                            a_branch = str(row_a.get("Филиал", "")).strip()
                            a_contract = str(row_a.get("Договор", "")).strip()
                            a_notes = str(row_a.get("Примечания", "")).strip()
                            
                            b_year = None
                            if a_bdate:
                                try:
                                    if len(a_bdate) == 4 and a_bdate.isdigit():
                                        b_year = int(a_bdate)
                                    elif "." in a_bdate:
                                        b_year = int(a_bdate.split(".")[-1])
                                except:
                                    pass
                                    
                            is_sport = "спортивный" in a_rank.lower() or a_rank in ["КМС", "МС", "МСМК"]
                            rank_type_str = "Спортивный" if is_sport else "Юношеский"
                            
                            f_lower = a_fio.lower()
                            if f_lower in stu_map:
                                stu = stu_map[f_lower]
                                stu["has_rank"] = True
                                if "ranks" not in stu:
                                    stu["ranks"] = []
                                if a_rank not in stu["ranks"]:
                                    stu["ranks"].append(a_rank)
                                if not a_bdate and stu.get("birth_date"):
                                    a_bdate = stu["birth_date"]
                                if not b_year and stu.get("birth_year"):
                                    b_year = stu["birth_year"]
                                if not a_branch and stu.get("branch"):
                                    a_branch = stu["branch"]
                                if not a_contract and stu.get("contract"):
                                    a_contract = stu["contract"]
                                    
                            ath_entry = {
                                "fio": a_fio,
                                "birth_year": b_year or "",
                                "rank": a_rank,
                                "rank_type": rank_type_str,
                                "order_num": in_order_num.strip(),
                                "order_date": date_str,
                                "org": in_org.strip(),
                                "city": in_city.strip(),
                                "competition": in_subj.strip(),
                                "discipline": in_disc.strip(),
                                "place": in_base_place.strip(),
                                "club": a_branch or "РФСОО «Федерация гонок дронов РО»",
                                "notes": a_notes,
                                "birth_date": a_bdate,
                                "student_branch": a_branch,
                                "student_contract": a_contract
                            }
                            new_athletes_entries.append(ath_entry)
                            
                        current_data["athletes"] = new_athletes_entries + current_data["athletes"]
                        
                        pg_msg = ""
                        if is_postgres_active:
                            ok_pg = save_order_and_athletes_to_postgres(new_order_entry, new_athletes_entries)
                            if ok_pg:
                                pg_msg = "🟢 Записано в базу данных PostgreSQL!"
                            else:
                                pg_msg = "⚠️ Не удалось сохранить в PostgreSQL, сохранено в локальные файлы."
                                
                        save_registry_files(current_data, base_dir=BASE_DIR)
                        
                        st.cache_data.clear()
                        st.session_state["order_athletes_list"] = [
                            {"ФИО": "", "Разряд": "1 юношеский разряд", "Дата рождения": "", "Филиал": "", "Договор": "", "Примечания": ""}
                        ]
                        
                        pg_info = f"\n\n{pg_msg}" if pg_msg else ""
                        st.success(f"🎉 Приказ **{in_order_num}** успешно сохранен! Добавлено **{len(valid_athletes)}** спортсменов.{pg_info}")
                        st.button("🔄 Обновить страницу и увидеть данные в реестре", on_click=lambda: st.rerun())
