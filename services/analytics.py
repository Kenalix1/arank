import pandas as pd
import plotly.express as px
from services.ranks import determine_rank_type

def create_ranks_bar_chart(df_athletes: pd.DataFrame):
    """Generates bar chart for distribution of assigned ranks and judging categories."""
    rank_only = df_athletes[df_athletes["rank"] != "Без разряда"]
    if rank_only.empty:
        return None
    rank_counts = rank_only["rank"].value_counts().reset_index()
    rank_counts.columns = ["Разряд / Категория", "Количество"]
    fig = px.bar(
        rank_counts,
        x="Разряд / Категория",
        y="Количество",
        color="Разряд / Категория",
        title="<b>Распределение спортивных разрядов и судейских категорий</b>",
        text="Количество",
        template="plotly_dark",
        color_discrete_sequence=['#3B82F6', '#10B981', '#6366F1', '#F59E0B', '#8B5CF6', '#14B8A6']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
    )
    return fig

def create_qualification_types_pie_chart(df_athletes: pd.DataFrame):
    """Generates donut chart for qualification types (Sports vs Junior vs Judges)."""
    rank_only = df_athletes[df_athletes["rank"] != "Без разряда"].copy()
    if rank_only.empty:
        return None
    rank_only["type_norm"] = rank_only["rank"].map(determine_rank_type)
    type_counts = rank_only["type_norm"].value_counts().reset_index()
    type_counts.columns = ["Тип квалификации", "Количество"]
    
    color_map = {
        "Спортивный": "#818CF8",
        "Юношеский": "#F59E0B",
        "Судейская категория": "#10B981"
    }
    
    fig = px.pie(
        type_counts,
        names="Тип квалификации",
        values="Количество",
        title="<b>Соотношение квалификаций: Спорт vs Судьи</b>",
        hole=0.45,
        template="plotly_dark",
        color="Тип квалификации",
        color_discrete_map=color_map
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
    )
    return fig

def create_branches_pie_chart(df_students: pd.DataFrame, df_athletes: pd.DataFrame = None):
    """Generates donut/pie chart for Academy student branches or athlete cities."""
    if df_students is not None and not df_students.empty:
        branch_data = df_students["branch"].apply(
            lambda b: "Аксай" if "аксай" in str(b).lower() else ("Пушкинская" if "пушкинская" in str(b).lower() else "Другое")
        )
        b_counts = branch_data.value_counts().reset_index()
        b_counts.columns = ["Филиал", "Учеников"]
        fig = px.pie(
            b_counts,
            names="Филиал",
            values="Учеников",
            title="<b>Распределение учеников Академии по филиалам</b>",
            hole=0.5,
            template="plotly_dark",
            color_discrete_sequence=['#2563EB', '#0D9488', '#F59E0B']
        )
    elif df_athletes is not None and not df_athletes.empty:
        city_counts = df_athletes["city"].value_counts().reset_index()
        city_counts.columns = ["Город", "Количество"]
        fig = px.pie(
            city_counts,
            names="Город",
            values="Количество",
            title="<b>Распределение по городам</b>",
            template="plotly_dark"
        )
    else:
        return None

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
    )
    return fig

def create_age_distribution_chart(df_athletes: pd.DataFrame):
    """Generates bar chart for athlete birth year / age distribution."""
    if df_athletes is None or df_athletes.empty:
        return None
    valid_years = df_athletes[df_athletes["birth_year"] != ""]["birth_year"].dropna().astype(int)
    valid_years = valid_years[valid_years >= 1975]
    if valid_years.empty:
        return None
    year_counts = valid_years.value_counts().sort_index().reset_index()
    year_counts.columns = ["Год рождения", "Количество"]
    fig = px.bar(
        year_counts,
        x="Год рождения",
        y="Количество",
        title="<b>Возрастной состав: распределение по годам рождения</b>",
        text="Количество",
        template="plotly_dark",
        color_discrete_sequence=['#6366F1']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", color="#E2E8F0")
    )
    return fig
