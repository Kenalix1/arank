import streamlit as st
import pandas as pd

def render_kpi_metrics(df_athletes: pd.DataFrame, df_students: pd.DataFrame):
    """Renders the top 6 summary KPI cards."""
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
