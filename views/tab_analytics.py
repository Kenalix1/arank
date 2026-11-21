import streamlit as st
import pandas as pd
from services.analytics import (
    create_ranks_bar_chart,
    create_qualification_types_pie_chart,
    create_branches_pie_chart,
    create_age_distribution_chart
)

def render_analytics_tab(df_athletes: pd.DataFrame, df_students: pd.DataFrame):
    """Renders Tab 4: Аналитика квалификаций (спортивные и судейские) и распределения."""
    st.markdown("#### Аналитический обзор квалификаций и категорий")
    
    col_chart1, col_chart2 = st.columns(2, gap="medium")
    
    with col_chart1:
        with st.container(border=True):
            fig1 = create_ranks_bar_chart(df_athletes)
            if fig1:
                st.plotly_chart(fig1, width='stretch')
            else:
                st.info("Нет данных по разрядам и категориям.")
        
    with col_chart2:
        with st.container(border=True):
            fig_types = create_qualification_types_pie_chart(df_athletes)
            if fig_types:
                st.plotly_chart(fig_types, width='stretch')
            else:
                fig2 = create_branches_pie_chart(df_students, df_athletes)
                if fig2:
                    st.plotly_chart(fig2, width='stretch')
                else:
                    st.info("Нет данных для отображения.")
        
    col_chart3, col_chart4 = st.columns(2, gap="medium")
    with col_chart3:
        with st.container(border=True):
            fig2 = create_branches_pie_chart(df_students, df_athletes)
            if fig2:
                st.plotly_chart(fig2, width='stretch')
            else:
                st.info("Нет данных по филиалам / городам.")
                
    with col_chart4:
        with st.container(border=True):
            fig3 = create_age_distribution_chart(df_athletes)
            if fig3:
                st.plotly_chart(fig3, width='stretch')
            else:
                st.info("Нет данных по годам рождения.")
