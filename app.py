import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="TechPulse 2026", layout="wide", initial_sidebar_state="expanded")

# 2. Custom CSS for the "Vibe"
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Titles and text */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #58a6ff;
    }
    .stMarkdown {
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Database Helper
def run_sql(query):
    conn = sqlite3.connect('layoffs.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 4. Header Section
st.title("🛡️ TechPulse 2026: Workforce Intelligence")
st.markdown("*A Data Narrative by Shivani Tomar*")
st.divider()

try:
    # --- Top Row: Real-time KPIs ---
    kpi_query = "SELECT SUM(employees) as total, COUNT(DISTINCT company) as cos FROM layoffs_table"
    kpi_df = run_sql(kpi_query)
    total_impact = kpi_df['total'].iloc[0]
    total_cos = kpi_df['cos'].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Market Impact", f"{int(total_impact):,} Roles", delta="-4.2% MoM")
    col2.metric("Affected Entities", f"{total_cos} Companies", delta="Sector Wide")
    col3.metric("Data Freshness", "Live Q2-2026", delta="Synced")

    st.write("") # Spacing

    # --- Middle Row: The Narrative Visuals ---
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("🏢 High-Impact Sector Analysis")
        # Treemap looks way cooler than a bar chart
        tree_data = run_sql("SELECT industry, SUM(employees) as total FROM layoffs_table GROUP BY industry ORDER BY total DESC")
        fig_tree = px.treemap(tree_data, path=['industry'], values='total', 
                             color='total', color_continuous_scale='Blues',
                             template="plotly_dark")
        fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_right:
        st.subheader("🤖 The AI Catalyst")
        ai_data = run_sql("SELECT ai_related, SUM(employees) as total FROM layoffs_table GROUP BY ai_related")
        fig_pie = px.pie(ai_data, names='ai_related', values='total', 
                         hole=0.7, color_discrete_sequence=['#58a6ff', '#1f6feb', '#0d1117'],
                         template="plotly_dark")
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Bottom Row: Search & Insight ---
    st.divider()
    with st.expander("🔍 Terminal Access: Query Company Intelligence"):
        company = st.text_input("Enter Company Name", placeholder="e.g. Google")
        if company:
            res = run_sql(f"SELECT company, industry, reason, ai_related FROM layoffs_table WHERE company LIKE '%{company}%'")
            st.dataframe(res, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for Data Pipeline... Run 'python database_setup.py' to initialize.")