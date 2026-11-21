import streamlit as st

def render_hero_banner():
    """Renders the top dark glassmorphism hero banner."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🛸 Официальный портал квалификаций</div>
        <div class="hero-title">Единый реестр спортсменов, судей и разрядов</div>
        <div class="hero-subtitle">
            Официальные приказы ведомств и федерации, спортивные разряды, судейские квалификационные категории и база обучающихся Академии пилотов «АтмоС» по гонкам дронов (беспилотных воздушных судов).
        </div>
    </div>
    """, unsafe_allow_html=True)
