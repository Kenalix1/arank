import streamlit as st
import pandas as pd
from services.athletes import get_initials
from services.ranks import (
    get_highest_sport_rank_record,
    get_highest_judge_rank_record,
    is_judge_rank,
    determine_rank_type
)

def render_dossier_tab(df_athletes: pd.DataFrame):
    """Renders Tab 5: Персональная карточка спортсмена / судьи / ученика."""
    st.markdown("#### Персональная карточка спортсмена / судьи / ученика")
    
    if df_athletes.empty:
        st.info("Нет данных о спортсменах.")
        return

    all_names = sorted(df_athletes["fio"].unique().tolist())
    default_idx = all_names.index("Хлыбов Василий Васильевич") if "Хлыбов Василий Васильевич" in all_names else 0
    selected_person = st.selectbox("Выберите пилота / судью из списка:", options=all_names, index=default_idx)
    
    if not selected_person:
        return

    records = df_athletes[df_athletes["fio"] == selected_person]
    first_r = records.iloc[0]
    initials = get_initials(selected_person)
    
    ranks_records = records[records["rank"] != "Без разряда"]
    best_sport = get_highest_sport_rank_record(ranks_records)
    best_judge = get_highest_judge_rank_record(ranks_records)
    
    # Generate badges for sports and/or judge qualifications
    pills_html = []
    if best_sport is not None:
        s_rank = best_sport["rank"]
        pill_class = "rank-pill-sport" if ("спортивный" in s_rank.lower() or s_rank in ["КМС", "МС", "МСМК"]) else "rank-pill-junior"
        pills_html.append(f'<span class="rank-pill {pill_class}">🏆 {s_rank}</span>')
        
    if best_judge is not None:
        j_rank = best_judge["rank"]
        pills_html.append(f'<span class="rank-pill rank-pill-judge">⚖️ {j_rank}</span>')
        
    if not pills_html:
        pills_html.append('<span class="rank-pill rank-pill-none">⏳ Обучается в Академии</span>')
        
    badges_rendered = " ".join(pills_html)
    
    # Profile Header Card Dark
    st.markdown(f"""
    <div class="profile-card">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="avatar-circle">{initials}</div>
            <div>
                <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #F8FAFC;">{selected_person}</h2>
                <div style="margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap;">
                    {badges_rendered}
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
        st.markdown("##### 📜 Хронология присвоения спортивных разрядов и судейских категорий:")
        hist_sorted = ranks_records.copy()
        hist_sorted["parsed_date"] = pd.to_datetime(hist_sorted["order_date"], format="%d.%m.%Y", errors="coerce")
        hist_sorted = hist_sorted.sort_values(by="parsed_date", ascending=False)
        for idx, r in hist_sorted.iterrows():
            place_str = f" ({r['place']})" if r['place'] else ""
            notes_str = f" • *{r['notes']}*" if r['notes'] else ""
            club_str = f" • {r['club']}" if r['club'] else ""
            
            is_j = is_judge_rank(r["rank"])
            item_class = "timeline-item timeline-item-judge" if is_j else "timeline-item"
            icon = "⚖️" if is_j else ("🏆" if r.get("rank_type") == "Спортивный" else "🎖️")
            type_label = determine_rank_type(r["rank"])
            
            st.markdown(f"""
            <div class="{item_class}">
                <div style="font-size: 0.82rem; font-weight: 600; color: #94A3B8;">{r['order_date']}</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #F1F5F9; margin-top: 2px;">
                    {icon} {r['rank']} <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">({type_label})</span>
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
            st.info("ℹ️ У данного участника пока нет присвоенных официальных разрядов или судейских категорий. Он проходит программу подготовки в Академии пилотов.")
