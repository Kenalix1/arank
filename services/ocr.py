import re
import os
import json
import base64
import logging
import requests
import streamlit as st
import pandas as pd
from config import KNOWN_RANKS

logger = logging.getLogger(__name__)

RUSSIAN_MONTHS = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}

def dative_to_nominative(word: str) -> str:
    """Converts a single Russian word (surname, name, patronymic) from dative/genitive to nominative."""
    if not word:
        return ""
    w = word.strip()
    
    # Patronymics
    if w.endswith('ичу'):
        return w[:-1] # Алексеевичу -> Алексеевич
    if w.endswith('евне') or w.endswith('овне') or w.endswith('ичне'):
        return w[:-1] + 'а' # Игоревне -> Игоревна, Александровне -> Александровна
        
    # Surnames
    if w.endswith('овой') or w.endswith('евой') or w.endswith('иной') or w.endswith('ыной'):
        return w[:-2] + 'а' # Аристарховой -> Аристархова, Горбачевой -> Горбачева
    if w.endswith('ову') or w.endswith('еву') or w.endswith('ину') or w.endswith('ыну'):
        return w[:-1] # Иванову -> Иванов, Сазонову -> Сазонов
    if w.endswith('скому') or w.endswith('цкому'):
        return w[:-2] + 'ий' # Бельскому -> Бельский
        
    # First names
    if w.endswith('аву'):
        return w[:-1] # Станиславу -> Станислав, Ярославу -> Ярослав
    if w.endswith('илу'):
        return w[:-1] # Кириллу -> Кирилл, Даниилу -> Даниил
    if w.endswith('ине'):
        return w[:-1] + 'а' # Полине -> Полина, Эвелине -> Эвелина, Марине -> Марина
    if w.endswith('ии'):
        return w[:-1] + 'я' # Марии -> Мария
    if w.endswith('ью'):
        return w[:-1] # Игорю -> Игорь
    if w.endswith('ею'):
        return w[:-1] # Сергею -> Сергей
    if w.endswith('ёму'):
        return w[:-1] # Артёму -> Артём
    if w.endswith('ему'):
        return w[:-1] # Артёму -> Артём
    if w.endswith('е'):
        return w[:-1] + 'а' # Анне -> Анна, Вере -> Вера
    if w.endswith('у'):
        return w[:-1] # Олегу -> Олег, Роману -> Роман
        
    return w

def normalize_name(fio_str: str, student_names: list = None) -> str:
    """Normalizes Russian full name to nominative case, matching with student DB if possible."""
    clean_fio = " ".join(fio_str.replace("•", "").replace("-", " ").strip().split())
    if not clean_fio:
        return ""
        
    # Check direct match with student DB
    if student_names:
        clean_lower = clean_fio.lower()
        for s_name in student_names:
            if s_name.lower() == clean_lower:
                return s_name
                
    parts = clean_fio.split()
    nom_parts = [dative_to_nominative(p) for p in parts]
    nom_fio = " ".join(nom_parts)
    
    # Check match with student DB again
    if student_names:
        nom_lower = nom_fio.lower()
        for s_name in student_names:
            if s_name.lower() == nom_lower:
                return s_name
        # Match by surname
        surname = parts[0].lower()
        for s_name in student_names:
            s_parts = s_name.split()
            if s_parts and s_parts[0].lower() == surname:
                # Same surname, check initials or partial
                if len(parts) >= 2 and len(s_parts) >= 2 and parts[1][0].lower() == s_parts[1][0].lower():
                    return s_name
                    
    return nom_fio

def normalize_rank_str(r_str: str) -> str:
    """Maps recognized rank text to official standard KNOWN_RANKS."""
    if not r_str:
        return "1 юношеский разряд"
    r_low = r_str.lower()
    
    # Referee / Judge categories
    if 'судь' in r_low or 'юсс' in r_low or 'ссвк' in r_low:
        if 'всеросс' in r_low or 'ссвк' in r_low:
            return 'Спортивный судья всероссийской категории'
        if 'перв' in r_low or '1' in r_low:
            return 'Спортивный судья первой категории'
        if 'втор' in r_low or '2' in r_low:
            return 'Спортивный судья второй категории'
        if 'трет' in r_low or '3' in r_low:
            return 'Спортивный судья третьей категории'
        if 'юн' in r_low or 'юсс' in r_low:
            return 'Юный спортивный судья'
        return 'Спортивный судья третьей категории'
        
    # Junior ranks
    if 'юношеск' in r_low:
        if '1' in r_low or 'перв' in r_low:
            return '1 юношеский разряд'
        if '2' in r_low or 'втор' in r_low:
            return '2 юношеский разряд'
        if '3' in r_low or 'трет' in r_low:
            return '3 юношеский разряд'
        return '1 юношеский разряд'
        
    # High titles
    if 'кмс' in r_low:
        return 'КМС'
    if 'мсмк' in r_low:
        return 'МСМК'
    if 'мс' in r_low or 'мастер' in r_low:
        return 'МС'
        
    # Adult sports ranks
    if 'спортивн' in r_low or 'разряд' in r_low:
        if '1' in r_low or 'перв' in r_low:
            return '1 спортивный разряд'
        if '2' in r_low or 'втор' in r_low:
            return '2 спортивный разряд'
        if '3' in r_low or 'трет' in r_low or 'iii' in r_low:
            return '3 спортивный разряд'
        return '3 спортивный разряд'
        
    return '1 юношеский разряд'

def get_gemini_api_key() -> str:
    """Retrieves Google Gemini API key from session state, secrets, or environment."""
    if "custom_gemini_api_key" in st.session_state and st.session_state["custom_gemini_api_key"]:
        return st.session_state["custom_gemini_api_key"].strip()
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

def parse_order_with_gemini(image_bytes: bytes, mime_type: str, api_key: str) -> dict:
    """Uses Google Gemini Flash Vision API to parse document image into structured order data."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = (
        "Ты — помощник секретаря спортивной федерации. Распознай официальный приказ на фото/скане "
        "о присвоении спортивных или юношеских разрядов либо квалификационных категорий спортивных судей.\n"
        "ВАЖНО:\n"
        "1. ФИО спортсменов/судей переведи строго в ИМЕНИТЕЛЬНЫЙ ПАДЕЖ (например: 'Горбачевой Полине Александровне' -> 'Горбачева Полина Александровна')\n"
        "2. Номер приказа извлеки точно (например: '№ 124-ПСР', '№ 16-ФГДРО', '№ 302-ПСР' и т.п.)\n"
        "3. Дату укажи строго в формате ДД.ММ.ГГГГ\n"
        "4. Разряды и категории нормализуй (например: '3 спортивный разряд', '1 юношеский разряд', 'Спортивный судья третьей категории')\n\n"
        "Верни результат СТРОГО в формате JSON:\n"
        "{\n"
        '  "order_num": "№ ...",\n'
        '  "order_date": "ДД.ММ.ГГГГ",\n'
        '  "org": "наименование органа/федерации",\n'
        '  "city": "город (например: г. Ростов-на-Дону)",\n'
        '  "subj": "предмет приказа",\n'
        '  "discipline": "Гонки дронов или Судейство соревнований",\n'
        '  "base_place": "Выполнение нормы ЕВСК / Квалификационные требования",\n'
        '  "athletes": [\n'
        '    {\n'
        '      "fio": "Фамилия Имя Отчество",\n'
        '      "rank": "разряд или судейская категория",\n'
        '      "birth_date": "ДД.ММ.ГГГГ или год",\n'
        '      "notes": ""\n'
        '    }\n'
        '  ]\n'
        "}"
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": b64_img}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    # Try gemini-2.0-flash first, fallback to gemini-1.5-flash
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code != 200:
        url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        resp = requests.post(url_fallback, json=payload, timeout=30)
        
    if resp.status_code != 200:
        raise Exception(f"Gemini API error ({resp.status_code}): {resp.text}")
        
    data = resp.json()
    content_text = data["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(content_text)
    return parsed

def parse_order_with_ocr_space(image_bytes: bytes, mime_type: str, api_key: str = "helloworld") -> str:
    """Uses free OCR.space engine to extract Russian text from image."""
    resp = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("document.jpg", image_bytes, mime_type)},
        data={"apikey": api_key, "language": "rus", "isTable": True},
        timeout=30
    )
    if resp.status_code != 200:
        raise Exception(f"OCR service error ({resp.status_code})")
    res_json = resp.json()
    if res_json.get("IsErroredOnProcessing", False):
        error_msg = res_json.get("ErrorMessage", ["OCR Error"])[0]
        raise Exception(error_msg)
    parsed_results = res_json.get("ParsedResults", [])
    if not parsed_results:
        return ""
    return parsed_results[0].get("ParsedText", "")

def parse_order_text(raw_text: str, student_names: list = None) -> dict:
    """
    Parses unstructured OCR text of an official order and extracts:
    order_num, order_date, city, org, subj, discipline, base_place, athletes
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    full_text = "\n".join(lines)
    
    # 1. Order Number
    num_match = re.search(r'(?:№|J°|No|Nº)\s*([0-9]+[\s-]*[А-Яа-яA-Za-z0-9/-]*)', full_text)
    if num_match:
        raw_num = num_match.group(1).replace(" ", "")
        order_num = f"№ {raw_num}"
    else:
        order_num = "б/н"
        
    # 2. Date
    order_date = ""
    # Pattern: «21» апреля 2026
    date_word_m = re.search(r'«?(\d{1,2})»?\s*([а-яё]+)\s*(\d{4})', full_text, re.IGNORECASE)
    if date_word_m:
        d_val = int(date_word_m.group(1))
        mo_str = date_word_m.group(2).lower()
        y_val = date_word_m.group(3)
        mo_num = RUSSIAN_MONTHS.get(mo_str)
        if mo_num:
            order_date = f"{d_val:02d}.{mo_num}.{y_val}"
            
    if not order_date:
        date_dot_m = re.search(r'(\d{2}\.\d{2}\.\d{4})', full_text)
        if date_dot_m:
            order_date = date_dot_m.group(1)
            
    # 3. City
    city = "г. Ростов-на-Дону"
    city_checks = [
        ("Ростов", "г. Ростов-на-Дону"),
        ("Батайск", "г. Батайск"),
        ("Азов", "г. Азов"),
        ("Аксай", "Аксайский район"),
        ("Новочеркасск", "г. Новочеркасск"),
        ("Таганрог", "г. Таганрог"),
        ("Шахты", "г. Шахты")
    ]
    for pattern, official_city in city_checks:
        if pattern.lower() in full_text.lower():
            city = official_city
            break
            
    # 4. Organization
    org = "РФСОО «Федерация гонок дронов Ростовской области»"
    if "уфкс" in full_text.lower() or "управление по физической культуре" in full_text.lower():
        org = "УФКС г. Ростова-на-Дону" if "ростов" in city.lower() else f"УФКС {city}"
    elif "аксай" in full_text.lower() and "администраци" in full_text.lower():
        org = "Отдел по ФКСиТ Администрации Аксайского района"
    elif "азов" in full_text.lower() and "администраци" in full_text.lower():
        org = "Отдел по ФК и спорту Администрации г. Азова"
    elif "новочеркасск" in full_text.lower() and "администраци" in full_text.lower():
        org = "УФКС Администрации г. Новочеркасска"
    elif "федерация" in full_text.lower():
        org = "РФСОО «Федерация гонок дронов Ростовской области»"
        
    # 5. Default Rank detected in order preamble
    default_rank = "3 спортивный разряд"
    rank_preamble_match = re.search(
        r'(?:присвоить|квалификаци[юи]|разряд[а-я]*)\s+([а-я0-9\s]{3,35}(?:разряд|категори[ию]|судь[а-я]+))',
        full_text,
        re.IGNORECASE
    )
    if rank_preamble_match:
        default_rank = normalize_rank_str(rank_preamble_match.group(1))
    elif "судь" in full_text.lower() or "судейск" in full_text.lower():
        default_rank = normalize_rank_str(full_text)
        
    is_judge = "судья" in default_rank.lower() or "категори" in default_rank.lower()
    discipline = "Судейство соревнований" if is_judge else "Гонки дронов"
    subj = f"Присвоение квалификации ({default_rank}) по виду спорта «гонки дронов»"
    
    # 6. Athletes / Judges List
    athletes = []
    
    # Scan for person rows (bullet points, numbers, or names)
    person_pattern = re.compile(
        r'(?:•|\*|-|\d+[\.)])\s*([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){1,2})(?:[,\s-]+(\d{2}\.\d{2}\.\d{4}|\d{4}))?',
        re.MULTILINE
    )
    
    matches = person_pattern.findall(full_text)
    for m in matches:
        raw_fio = m[0].strip()
        raw_date = m[1].strip() if len(m) > 1 else ""
        
        # Filter false positives like "Исполнением Приказа", "Начальника Управления"
        forbidden = ["начальник", "приказ", "управлен", "федераци", "министерств", "контроль", "копия", "верно"]
        if any(f in raw_fio.lower() for f in forbidden):
            continue
            
        norm_fio = normalize_name(raw_fio, student_names=student_names)
        
        # Check if rank is specified on the same line
        athletes.append({
            "fio": norm_fio,
            "rank": default_rank,
            "birth_date": raw_date,
            "notes": ""
        })
        
    return {
        "order_num": order_num,
        "order_date": order_date,
        "city": city,
        "org": org,
        "subj": subj,
        "discipline": discipline,
        "base_place": "Выполнение нормы ЕВСК / Квалификационные требования",
        "athletes": athletes
    }

def recognize_and_parse_document(
    image_bytes: bytes,
    mime_type: str,
    gemini_api_key: str = None,
    df_students: pd.DataFrame = None
) -> tuple[dict, str]:
    """
    High-level OCR & structured extraction pipeline:
    1. If Gemini API Key available -> Google Gemini Vision AI
    2. Else -> Free OCR.space Vision Engine + Regex Parser
    Matches and enriches with student database.
    """
    student_names = df_students["fio"].tolist() if df_students is not None and not df_students.empty else []
    
    if gemini_api_key:
        try:
            parsed = parse_order_with_gemini(image_bytes, mime_type, gemini_api_key)
            return parsed, "Google Gemini Vision AI"
        except Exception as e:
            logger.warning(f"Gemini OCR failed, trying OCR.space fallback: {e}")
            
    # Fallback to OCR.space
    try:
        raw_text = parse_order_with_ocr_space(image_bytes, mime_type)
        if raw_text:
            parsed = parse_order_text(raw_text, student_names=student_names)
            return parsed, "OCR.space Vision Engine"
    except Exception as e:
        logger.error(f"OCR.space failed: {e}")
        
    return {}, "Не удалось распознать"
