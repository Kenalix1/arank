import os
import json
import pandas as pd
from config import BASE_DIR, JSON_FILE, XLSX_FILE, CSV_FILE, MD_FILE

def save_registry_files(json_data: dict, base_dir: str = BASE_DIR):
    """
    Synchronously updates local backup and export files:
    - Реестр_приказов_и_разрядов.json
    - Реестр_приказов_и_разрядов.csv
    - Реестр_приказов_и_разрядов.xlsx
    - Реестр_приказов_и_разрядов.md
    """
    json_path = os.path.join(base_dir, "Реестр_приказов_и_разрядов.json")
    xlsx_path = os.path.join(base_dir, "Реестр_приказов_и_разрядов.xlsx")
    csv_path = os.path.join(base_dir, "Реестр_приказов_и_разрядов.csv")
    md_path = os.path.join(base_dir, "Реестр_приказов_и_разрядов.md")

    # 1. JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    df_ath = pd.DataFrame(json_data["athletes"])
    df_ord = pd.DataFrame(json_data["orders"])
    df_stu = pd.DataFrame(json_data.get("students", []))

    # 2. CSV
    cols_csv = {
        "fio": "ФИО спортсмена / ученика",
        "birth": "Дата / Год рожд.",
        "rank": "Присвоенный разряд / Статус",
        "rank_type": "Категория",
        "order_num": "Номер приказа",
        "order_date": "Дата приказа",
        "org": "Орган / Организация",
        "city": "Город",
        "competition": "Основание / Соревнование",
        "discipline": "Дисциплина",
        "place": "Результат / Статус",
        "club": "Филиал / Клуб",
        "notes": "Примечания / Договор"
    }
    df_c = df_ath.copy()
    df_c["birth"] = df_c.apply(lambda r: str(r.get("birth_date") or r.get("birth_year") or "-"), axis=1)
    df_c["№ п/п"] = range(1, len(df_c) + 1)
    csv_out = df_c[["№ п/п"] + list(cols_csv.keys())].rename(columns=cols_csv)
    csv_out.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    # 3. XLSX
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        csv_out.to_excel(writer, sheet_name="Сводный реестр", index=False)
        sport_df = csv_out[csv_out["Категория"] == "Спортивный"]
        sport_df.to_excel(writer, sheet_name="Спортивные разряды", index=False)
        junior_df = csv_out[csv_out["Категория"] == "Юношеский"]
        junior_df.to_excel(writer, sheet_name="Юношеские разряды", index=False)
        if not df_stu.empty:
            stu_out = df_stu.copy()
            stu_out["Присвоенные разряды"] = stu_out["ranks"].apply(lambda r: ", ".join(r) if r else "-")
            stu_out.to_excel(writer, sheet_name="Ученики Академии", index=False)
        if not df_ord.empty:
            df_ord.to_excel(writer, sheet_name="Приказы (документы)", index=False)

    # 4. MD
    total_ath = len(df_ath)
    total_orders = len(df_ord)
    sport_count = (df_ath["rank_type"] == "Спортивный").sum()
    junior_count = (df_ath["rank_type"] == "Юношеский").sum()

    md_lines = [
        "# Реестр приказов и присвоенных разрядов по гонкам дронов (БВС)",
        "",
        "Данные сформированы на основе фотокопий официальных приказов органов исполнительной власти в сфере спорта и региональной спортивной федерации РФСОО «Федерация гонок дронов Ростовской области».",
        "",
        "## Общая статистика",
        f"- **Всего записей о присвоениях:** {total_ath}",
        f"- **Всего документов (приказов/выписок):** {total_orders}",
        f"- **Спортивные разряды:** {sport_count}",
        f"- **Юношеские разряды:** {junior_count}",
        "",
        "## 1. Реестр документов (приказов)",
        "| № | Орган / Организация | Номер приказа | Дата | Город | Предмет приказа | Чел. | Файл(ы) фото |",
        "|---|---|---|---|---|---|---|---|"
    ]
    for idx, r in df_ord.iterrows():
        md_lines.append(f"| {idx+1} | {r.get('org','')} | {r.get('num','')} | {r.get('date','')} | {r.get('city','')} | {r.get('subj','')} | {r.get('count','')} | `{r.get('file','')}` |")

    md_lines.extend([
        "",
        "## 2. Сводный список присвоенных разрядов",
        "| № | ФИО | Год | Разряд | Приказ | Дата | Орган / Организация | Город | Соревнование / Основание | Дисциплина / Место | Клуб / Примечания |",
        "|---|---|---|---|---|---|---|---|---|---|---|"
    ])
    for idx, r in df_ath.iterrows():
        fio_b = f"**{r.get('fio','')}**"
        yr = str(r.get('birth_year') or '')
        rk = str(r.get('rank') or '')
        onum = str(r.get('order_num') or '')
        odate = str(r.get('order_date') or '')
        org = str(r.get('org') or '')
        cty = str(r.get('city') or '')
        comp = str(r.get('competition') or '')
        disc = f"{r.get('discipline','')} - {r.get('place','')}" if r.get('place') else str(r.get('discipline') or '')
        clb = str(r.get('club') or '')
        md_lines.append(f"| {idx+1} | {fio_b} | {yr} | {rk} | {onum} | {odate} | {org} | {cty} | {comp} | {disc} | {clb} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
