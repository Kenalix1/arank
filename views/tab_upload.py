import os
import json
from datetime import datetime, date
import streamlit as st
import pandas as pd
from config import BASE_DIR, PHOTOS_DIR, JSON_FILE, KNOWN_RANKS
from services.ranks import determine_rank_type
from services.ocr import (
    recognize_and_parse_document,
    parse_order_text,
    get_gemini_api_key,
    normalize_name
)
from database import save_order_and_athletes_to_postgres, save_registry_files

def render_upload_tab(df_students: pd.DataFrame, is_postgres_active: bool):
    """Renders Tab 6: Внесение приказа с авто-распознаванием по фото и ручной проверкой."""
    st.markdown("#### 📥 Авто-распознавание приказа по фото и внесение в базу")
    st.caption("Загрузите фотокопию или скан приказа — система автоматически распознает реквизиты, разряды и список участников, сопоставит их с базой учеников и предложит вам проверить и при необходимости внести ручные правки.")
    
    # Initialize session state for metadata and athletes
    if "order_athletes_list" not in st.session_state:
        st.session_state["order_athletes_list"] = [
            {"ФИО": "", "Разряд": "1 юношеский разряд", "Дата рождения": "", "Филиал": "", "Договор": "", "Примечания": ""}
        ]
        
    if "auto_order_num" not in st.session_state:
        st.session_state["auto_order_num"] = ""
    if "auto_order_date" not in st.session_state:
        st.session_state["auto_order_date"] = date.today()
    if "auto_city" not in st.session_state:
        st.session_state["auto_city"] = "г. Ростов-на-Дону"
    if "auto_org" not in st.session_state:
        st.session_state["auto_org"] = "РФСОО «Федерация гонок дронов Ростовской области»"
    if "auto_subj" not in st.session_state:
        st.session_state["auto_subj"] = "Присвоение спортивных / юношеских разрядов и судейских категорий по гонкам дронов"
    if "auto_disc" not in st.session_state:
        st.session_state["auto_disc"] = "Гонки дронов"
    if "auto_place" not in st.session_state:
        st.session_state["auto_place"] = "Выполнение нормы ЕВСК / Квалификационные требования"

    # ==========================================
    # 1. PHOTO UPLOAD & AUTOMATIC RECOGNITION
    # ==========================================
    with st.container(border=True):
        st.markdown("##### 1️⃣ Загрузка фото / скана документа и авто-распознавание")
        
        col_up1, col_up2 = st.columns([1, 1], gap="medium")
        
        with col_up1:
            uploaded_doc = st.file_uploader(
                "Прикрепите фото или скан приказа (JPG, PNG, PDF):",
                type=["jpg", "jpeg", "png", "webp", "pdf"],
                help="Файл сохраняется в каталог photos/ и прикрепляется к приказу в реестре.",
                key="uploaded_doc"
            )
            
            if uploaded_doc is not None and uploaded_doc.type.startswith("image/"):
                st.image(uploaded_doc, caption=f"Загруженный файл: {uploaded_doc.name}", width='stretch')
            elif uploaded_doc is not None:
                st.info(f"📄 Загружен документ: **{uploaded_doc.name}** ({round(uploaded_doc.size / 1024, 1)} КБ)")

        with col_up2:
            st.markdown("**Автоматическое извлечение данных из документа:**")
            st.caption("Система автоматически распознает номер, дату, организацию, город и таблицу спортсменов/судей с приведением ФИО к именительному падежу.")
            
            btn_auto_parse = st.button(
                "✨ АВТОМАТИЧЕСКИ РАСПОЗНАТЬ И ЗАПОЛНИТЬ ИЗ ФОТО",
                type="primary",
                width='stretch',
                disabled=(uploaded_doc is None),
                key="btn_run_auto_ocr"
            )
            
            with st.expander("⚙️ Настройка AI-модели (Google Gemini / Бесплатный OCR)", expanded=False):
                st.caption("По умолчанию работает встроенный бесплатный OCR-сервер. Для максимальной точности сложных сканов можно подключить бесплатный ключ Google Gemini Vision.")
                custom_key = st.text_input(
                    "Google Gemini API Key (необязательно):",
                    value=get_gemini_api_key(),
                    type="password",
                    help="Бесплатный ключ создаётся за 1 минуту на https://aistudio.google.com/",
                    key="input_gemini_api_key"
                )
                if custom_key:
                    st.session_state["custom_gemini_api_key"] = custom_key
                    
            with st.expander("📋 Или вставить распознанный текст вручную (Live Text)", expanded=False):
                pasted_text = st.text_area("Вставьте текст приказа из буфера:", height=100, placeholder="Скопируйте текст из фото на iPhone/Mac и вставьте сюда...")
                if st.button("Разобрать вставленный текст"):
                    if pasted_text.strip():
                        parsed = parse_order_text(pasted_text, student_names=df_students["fio"].tolist() if not df_students.empty else [])
                        _apply_parsed_data(parsed, df_students, "Ручной текст")
                        st.rerun()

            if btn_auto_parse and uploaded_doc is not None:
                with st.spinner("🔍 Сканирование документа, распознавание текста и распределение по полям..."):
                    img_bytes = uploaded_doc.getvalue()
                    mime_type = uploaded_doc.type or "image/jpeg"
                    gemini_key = get_gemini_api_key()
                    
                    parsed_result, engine_name = recognize_and_parse_document(
                        image_bytes=img_bytes,
                        mime_type=mime_type,
                        gemini_api_key=gemini_key,
                        df_students=df_students
                    )
                    
                    if parsed_result:
                        _apply_parsed_data(parsed_result, df_students, engine_name)
                        st.rerun()
                    else:
                        st.error("⚠️ Не удалось распознать документ автоматически. Проверьте четкость изображения или вставьте текст документа вручную.")

    # Show notification if recognition just succeeded
    if "ocr_notice" in st.session_state and st.session_state["ocr_notice"]:
        st.success(st.session_state["ocr_notice"])

    # ==========================================
    # 2. ORDER METADATA (EDITABLE)
    # ==========================================
    with st.container(border=True):
        st.markdown("##### 2️⃣ Реквизиты приказа (проверьте и при необходимости исправьте)")
        
        col_u1, col_u2, col_u3 = st.columns([1, 1, 1])
        with col_u1:
            in_order_num = st.text_input(
                "Номер приказа *",
                value=st.session_state.get("auto_order_num", ""),
                placeholder="например: № 124-ПСР или № 16-ФГДРО",
                key="in_order_num"
            )
        with col_u2:
            default_d = st.session_state.get("auto_order_date", date.today())
            if isinstance(default_d, str):
                try:
                    default_d = datetime.strptime(default_d, "%d.%m.%Y").date()
                except:
                    default_d = date.today()
            in_order_date = st.date_input(
                "Дата приказа *",
                value=default_d,
                format="DD.MM.YYYY",
                key="in_order_date"
            )
        with col_u3:
            city_suggestions = ["г. Ростов-на-Дону", "г. Батайск", "г. Азов", "г. Новочеркасск", "Аксайский район", "г. Таганрог", "г. Шахты"]
            cur_city = st.session_state.get("auto_city", "г. Ростов-на-Дону")
            city_idx = city_suggestions.index(cur_city) if cur_city in city_suggestions else len(city_suggestions)
            
            in_city = st.selectbox(
                "Город / Муниципалитет *",
                options=city_suggestions + ["Другой (ввести вручную)"],
                index=city_idx,
                key="in_city"
            )
            if in_city == "Другой (ввести вручную)":
                in_city = st.text_input("Введите город / район:", value=cur_city, key="in_city_custom")
                
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
            cur_org = st.session_state.get("auto_org", "РФСОО «Федерация гонок дронов Ростовской области»")
            org_idx = org_suggestions.index(cur_org) if cur_org in org_suggestions else len(org_suggestions)
            
            in_org = st.selectbox(
                "Орган власти / Федерация *",
                options=org_suggestions + ["Другая организация (ввести вручную)"],
                index=org_idx,
                key="in_org"
            )
            if in_org == "Другая организация (ввести вручную)":
                in_org = st.text_input("Введите наименование органа / федерации:", value=cur_org, key="in_org_custom")
                
        with col_u5:
            in_subj = st.text_input(
                "Предмет приказа / основание",
                value=st.session_state.get("auto_subj", "Присвоение спортивных / юношеских разрядов и судейских категорий по гонкам дронов"),
                key="in_subj"
            )
            
        col_u6, col_u7 = st.columns([1, 1])
        with col_u6:
            disc_suggestions = [
                "Гонки дронов",
                "Судейство соревнований",
                "Гонки дронов (класс 75 мм)",
                "Гонки дронов (класс 200 мм)",
                "Технический симулятор — гонки БВС"
            ]
            cur_disc = st.session_state.get("auto_disc", "Гонки дронов")
            disc_idx = disc_suggestions.index(cur_disc) if cur_disc in disc_suggestions else len(disc_suggestions)
            
            in_disc = st.selectbox(
                "Дисциплина / Направление (по умолчанию)",
                options=disc_suggestions + ["Другая"],
                index=disc_idx,
                key="in_disc"
            )
            if in_disc == "Другая":
                in_disc = st.text_input("Введите дисциплину:", value=cur_disc, key="in_disc_custom")
                
        with col_u7:
            in_base_place = st.text_input(
                "Основание / результат (по умолчанию)",
                value=st.session_state.get("auto_place", "Выполнение нормы ЕВСК / Квалификационные требования"),
                key="in_base_place"
            )

    # ==========================================
    # 3. ATHLETES & JUDGES TABLE (EDITABLE)
    # ==========================================
    with st.container(border=True):
        st.markdown("##### 3️⃣ Список участников и разрядов (проверьте и внесите правки)")
        st.caption("Таблица заполнена автоматически. Вы можете отредактировать любые ФИО, изменить разряд через список, добавить новые строки `+` или удалить ошибочные:")
        
        df_editor_input = pd.DataFrame(st.session_state["order_athletes_list"])
        
        edited_athletes_df = st.data_editor(
            df_editor_input,
            num_rows="dynamic",
            width='stretch',
            column_config={
                "ФИО": st.column_config.TextColumn("ФИО участника *", width="large", required=True),
                "Разряд": st.column_config.SelectboxColumn("Присваиваемый разряд / категория *", options=KNOWN_RANKS, required=True, width="medium"),
                "Дата рождения": st.column_config.TextColumn("Дата / Год рождения", width="medium"),
                "Филиал": st.column_config.TextColumn("Филиал / Клуб", width="medium"),
                "Договор": st.column_config.TextColumn("№ Договора", width="small"),
                "Примечания": st.column_config.TextColumn("Примечание", width="medium"),
            },
            key="editor_athletes"
        )

    # ==========================================
    # 4. SAVE TO DATABASE
    # ==========================================
    with st.container(border=True):
        st.markdown("##### 4️⃣ Сохранение проверенных данных в базу")
        
        if is_postgres_active:
            st.success("🟢 **База данных PostgreSQL подключена.** Приказ и разряды будут сохранены в таблицы PostgreSQL.")
        else:
            st.info("ℹ️ **Локальный режим (JSON / Excel / CSV).** Для постоянного подключения к PostgreSQL укажите `DATABASE_URL` в переменных окружения или `st.secrets`.")
            
        btn_save = st.button("💾 СОХРАНИТЬ ПРИКАЗ И РАЗРЯДЫ В БАЗУ ДАННЫХ", type="primary", width='stretch', key="btn_save_order")
            
        if btn_save:
            if not in_order_num.strip():
                st.error("Пожалуйста, укажите номер приказа (например: № 124-ПСР)!")
            else:
                valid_athletes = []
                for _, r in edited_athletes_df.iterrows():
                    fio_str = str(r.get("ФИО", "")).strip()
                    if fio_str and fio_str.lower() != "nan":
                        valid_athletes.append(r)
                        
                if not valid_athletes:
                    st.error("Пожалуйста, добавьте хотя бы одного человека в таблицу!")
                else:
                    with st.spinner("Сохранение приказа и квалификаций в базу данных..."):
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
                        
                        # 2. Add athletes/judges
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
                                    
                            rank_type_str = determine_rank_type(a_rank)
                            
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
                        
                        # Reset session state after save
                        st.cache_data.clear()
                        st.session_state["order_athletes_list"] = [
                            {"ФИО": "", "Разряд": "1 юношеский разряд", "Дата рождения": "", "Филиал": "", "Договор": "", "Примечания": ""}
                        ]
                        st.session_state["auto_order_num"] = ""
                        st.session_state["auto_order_date"] = date.today()
                        st.session_state["ocr_notice"] = ""
                        
                        pg_info = f"\n\n{pg_msg}" if pg_msg else ""
                        st.success(f"🎉 Приказ **{in_order_num}** успешно сохранен! Добавлено **{len(valid_athletes)}** записей.{pg_info}")
                        st.button("🔄 Обновить страницу и увидеть данные в реестре", on_click=lambda: st.rerun())

def _apply_parsed_data(parsed: dict, df_students: pd.DataFrame, engine_name: str):
    """Helper to populate session state from parsed dictionary."""
    if not parsed:
        return
        
    st.session_state["auto_order_num"] = parsed.get("order_num", "")
    
    date_str = parsed.get("order_date", "")
    if date_str:
        try:
            st.session_state["auto_order_date"] = datetime.strptime(date_str, "%d.%m.%Y").date()
        except:
            st.session_state["auto_order_date"] = date.today()
            
    if parsed.get("city"):
        st.session_state["auto_city"] = parsed.get("city")
    if parsed.get("org"):
        st.session_state["auto_org"] = parsed.get("org")
    if parsed.get("subj"):
        st.session_state["auto_subj"] = parsed.get("subj")
    if parsed.get("discipline"):
        st.session_state["auto_disc"] = parsed.get("discipline")
    if parsed.get("base_place"):
        st.session_state["auto_place"] = parsed.get("base_place")
        
    # Match students
    stu_lookup = {}
    if df_students is not None and not df_students.empty:
        for _, s_row in df_students.iterrows():
            clean_f = " ".join(str(s_row["fio"]).strip().split()).lower()
            stu_lookup[clean_f] = s_row
            
    parsed_athletes = parsed.get("athletes", [])
    athletes_rows = []
    
    for a in parsed_athletes:
        fio_val = normalize_name(a.get("fio", ""))
        rank_val = a.get("rank", "1 юношеский разряд")
        birth_val = a.get("birth_date", "")
        branch_val = ""
        contract_val = ""
        
        lookup_key = " ".join(fio_val.split()).lower()
        if lookup_key in stu_lookup:
            matched_s = stu_lookup[lookup_key]
            if not birth_val:
                birth_val = str(matched_s.get("birth_date") or matched_s.get("birth_year") or "")
            branch_val = str(matched_s.get("branch") or "")
            contract_val = str(matched_s.get("contract") or "")
            
        athletes_rows.append({
            "ФИО": fio_val,
            "Разряд": rank_val,
            "Дата рождения": birth_val,
            "Филиал": branch_val,
            "Договор": contract_val,
            "Примечания": a.get("notes", "")
        })
        
    if athletes_rows:
        st.session_state["order_athletes_list"] = athletes_rows
        
    st.session_state["ocr_notice"] = (
        f"🎯 Документ успешно распознан движком **{engine_name}**! "
        f"Найдено: **{len(athletes_rows)}** участников. Данные распределены по полям ниже — проверьте и внесите ручные правки при необходимости."
    )
