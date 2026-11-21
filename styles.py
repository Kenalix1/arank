import streamlit as st

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Dark Theme Background */
    .stApp {
        background-color: #090D16 !important;
        color: #F1F5F9;
    }

    /* Hero Banner Dark Glassmorphism */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #131C31 40%, #1E1B4B 100%);
        border-radius: 20px;
        padding: 32px 36px;
        color: #FFFFFF;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6), 0 0 25px rgba(59, 130, 246, 0.1);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(30, 58, 138, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(96, 165, 250, 0.3);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #60A5FA;
        margin-bottom: 12px;
    }
    
    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        background: linear-gradient(to right, #FFFFFF, #93C5FD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: #94A3B8;
        max-width: 800px;
        line-height: 1.5;
    }

    /* KPI Metrics Cards Dark */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 28px;
    }
    
    .kpi-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }
    
    .kpi-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 4px;
    }
    
    .kpi-num {
        font-size: 1.75rem;
        font-weight: 800;
        color: #F8FAFC;
    }

    /* Profile / Athlete Dossier Card */
    .profile-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .avatar-circle {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFFFFF;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .rank-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    
    .rank-pill-sport {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    
    .rank-pill-junior {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.35);
    }
    
    .rank-pill-none {
        background: rgba(148, 163, 184, 0.12);
        color: #94A3B8;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    /* Timeline Items in Dossier */
    .timeline-item {
        border-left: 2px solid #3B82F6;
        padding-left: 18px;
        padding-bottom: 20px;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -7px;
        top: 2px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #3B82F6;
        border: 2px solid #090D16;
        box-shadow: 0 0 8px #3B82F6;
    }

    /* Dark Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Container borders dark */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 14px !important;
    }

    /* Metric values dark */
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
</style>
"""

def inject_custom_css():
    """Injects custom CSS styling for dark theme glassmorphism."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
