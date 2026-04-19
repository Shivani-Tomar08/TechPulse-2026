import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechPulse 2026",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── THEME / CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0f1e;
    color: #e2e8f0;
}

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.block-container { padding: 2rem 2.5rem 2rem 2.5rem; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.5rem;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #475569;
    margin-top: 0.3rem;
}
.kpi-badge-red   { color: #f87171; font-weight: 600; }
.kpi-badge-green { color: #34d399; font-weight: 600; }
.kpi-badge-blue  { color: #60a5fa; font-weight: 600; }

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    border-left: 3px solid #3b82f6;
    padding-left: 0.75rem;
    margin: 1.8rem 0 1rem 0;
}

/* Insight box */
.insight-box {
    background: linear-gradient(135deg, #0f2027, #1a3a4a);
    border: 1px solid #0ea5e9;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    color: #bae6fd;
    margin-top: 0.5rem;
}

/* Company card */
.company-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #060c1a;
    border-right: 1px solid #1e293b;
}

/* Plotly chart background fix */
.js-plotly-plot .plotly { background: transparent !important; }

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
}

/* Tag chips */
.tag-chip {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px;
}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY DARK TEMPLATE ────────────────────────────────────────────────────
CHART_BG   = "rgba(0,0,0,0)"
PAPER_BG   = "rgba(0,0,0,0)"
GRID_COLOR = "#1e293b"
FONT_COLOR = "#94a3b8"
ACCENT     = ["#3b82f6", "#f87171", "#34d399", "#fbbf24", "#a78bfa", "#fb923c", "#22d3ee"]

def apply_dark(fig, height=320):
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", color=FONT_COLOR, size=12),
        height=height,
        margin=dict(t=20, l=10, r=10, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    return fig

# ─── DATA LAYER ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    conn = sqlite3.connect('layoffs.db')
    df = pd.read_sql("SELECT * FROM layoffs_table", conn, params=None)
    conn.close()
    df.columns = [c.lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['employees_laid_off'] = pd.to_numeric(df['employees_laid_off'], errors='coerce').fillna(0)
    df['total_employees']    = pd.to_numeric(df['total_employees'],    errors='coerce').fillna(0)
    df['percentage_workforce']= pd.to_numeric(df['percentage_workforce'], errors='coerce').fillna(0)
    df['severance_weeks']    = pd.to_numeric(df['severance_weeks'],    errors='coerce').fillna(0)
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    return df

df_full = load_data()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ TechPulse 2026")
    st.markdown("<div style='font-size:0.72rem;color:#475569;margin-bottom:1rem;'>Workforce Intelligence Platform</div>", unsafe_allow_html=True)
    st.divider()

    all_industries = sorted(df_full['industry'].dropna().unique().tolist())
    selected_industries = st.multiselect("Filter by Industry", all_industries, default=all_industries)

    all_countries = sorted(df_full['country'].dropna().unique().tolist())
    selected_countries = st.multiselect("Filter by Country", all_countries, default=all_countries)

    all_years = sorted(df_full['year'].dropna().unique().tolist())
    selected_years = st.multiselect("Filter by Year", all_years, default=all_years)

    ai_filter = st.selectbox("AI-Related Filter", ["All", "Yes", "No", "Partial"])

    st.divider()
    st.markdown("<div style='font-size:0.72rem;color:#475569;'>Shivani Tomar · Data Systems Analyst<br>Dataset: Tech Layoffs 2025–2026</div>", unsafe_allow_html=True)

# ─── APPLY FILTERS ───────────────────────────────────────────────────────────
df = df_full.copy()
if selected_industries:
    df = df[df['industry'].isin(selected_industries)]
if selected_countries:
    df = df[df['country'].isin(selected_countries)]
if selected_years:
    df = df[df['year'].isin(selected_years)]
if ai_filter != "All":
    df = df[df['ai_related'] == ai_filter]

if df.empty:
    st.warning("No data matches your current filters. Adjust the sidebar.")
    st.stop()

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("# TechPulse 2026")
st.markdown("<div style='color:#64748b;font-size:0.9rem;margin-bottom:1.5rem;'>Real-time workforce intelligence · Tech sector layoff analysis</div>", unsafe_allow_html=True)

# ─── KPI ROW ─────────────────────────────────────────────────────────────────
total_laid_off   = int(df['employees_laid_off'].sum())
total_companies  = df['company'].nunique()
avg_pct          = df['percentage_workforce'].mean()
ai_pct           = round(df[df['ai_related'] == 'Yes']['employees_laid_off'].sum() / df['employees_laid_off'].sum() * 100, 1)
avg_severance    = df['severance_weeks'].mean()

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>Total Laid Off</div>
        <div class='kpi-value'>{total_laid_off:,}</div>
        <div class='kpi-sub'>across all selected sectors</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>Companies Tracked</div>
        <div class='kpi-value'>{total_companies}</div>
        <div class='kpi-sub'>unique organizations</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>Avg Workforce Cut</div>
        <div class='kpi-value'>{avg_pct:.1f}%</div>
        <div class='kpi-sub kpi-badge-red'>per layoff event</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>AI-Driven Layoffs</div>
        <div class='kpi-value'>{ai_pct}%</div>
        <div class='kpi-sub kpi-badge-blue'>of total headcount</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>Avg Severance</div>
        <div class='kpi-value'>{avg_severance:.1f}w</div>
        <div class='kpi-sub kpi-badge-green'>weeks offered</div>
    </div>""", unsafe_allow_html=True)

# ─── SECTION 1: TIMELINE ─────────────────────────────────────────────────────
st.markdown("<div class='section-header'>01 · Layoff Timeline</div>", unsafe_allow_html=True)

timeline_df = df.groupby('year_month')['employees_laid_off'].sum().reset_index()
timeline_df.columns = ['Month', 'Laid Off']
timeline_df = timeline_df.sort_values('Month')

col_t1, col_t2 = st.columns([7, 3])

with col_t1:
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(
        x=timeline_df['Month'], y=timeline_df['Laid Off'],
        marker_color='#3b82f6', marker_line_width=0,
        name='Layoffs', opacity=0.85
    ))
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df['Month'], y=timeline_df['Laid Off'],
        mode='lines', line=dict(color='#60a5fa', width=2),
        name='Trend'
    ))
    fig_timeline = apply_dark(fig_timeline, height=280)
    fig_timeline.update_layout(showlegend=False, bargap=0.25)
    st.plotly_chart(fig_timeline, use_container_width=True)

with col_t2:
    peak_month = timeline_df.loc[timeline_df['Laid Off'].idxmax()]
    worst_company = df.loc[df['employees_laid_off'].idxmax()]
    st.markdown(f"""<div class='insight-box'>
        <b>📌 Peak Month</b><br>{peak_month['Month']}<br>
        <span style='font-size:1.1rem;font-weight:700;color:#f1f5f9'>{int(peak_month['Laid Off']):,}</span> roles cut<br><br>
        <b>📌 Single Largest Layoff</b><br>{worst_company['company']}<br>
        <span style='font-size:1.1rem;font-weight:700;color:#f1f5f9'>{int(worst_company['employees_laid_off']):,}</span> employees<br>
        <span style='color:#64748b;font-size:0.75rem;'>{worst_company['industry']} · {worst_company['date'].strftime('%b %Y')}</span>
    </div>""", unsafe_allow_html=True)

# ─── SECTION 2: SECTOR + AI BREAKDOWN ────────────────────────────────────────
st.markdown("<div class='section-header'>02 · Sector & AI Analysis</div>", unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns([4, 3, 3])

with col_s1:
    sector_df = df.groupby('industry')['employees_laid_off'].sum().reset_index().sort_values('employees_laid_off', ascending=True).tail(10)
    fig_sector = go.Figure(go.Bar(
        x=sector_df['employees_laid_off'], y=sector_df['industry'],
        orientation='h',
        marker=dict(
            color=sector_df['employees_laid_off'],
            colorscale=[[0, '#1e3a5f'], [1, '#3b82f6']],
            showscale=False
        )
    ))
    fig_sector = apply_dark(fig_sector, height=320)
    fig_sector.update_layout(title=dict(text="Top Sectors by Headcount", font=dict(size=12, color='#94a3b8')))
    st.plotly_chart(fig_sector, use_container_width=True)

with col_s2:
    ai_df = df.groupby('ai_related')['employees_laid_off'].sum().reset_index()
    fig_ai = px.pie(ai_df, names='ai_related', values='employees_laid_off',
                    hole=0.65,
                    color_discrete_map={'Yes': '#3b82f6', 'No': '#1e3a5f', 'Partial': '#0ea5e9'})
    fig_ai.update_traces(textposition='outside', textinfo='percent+label')
    fig_ai = apply_dark(fig_ai, height=320)
    fig_ai.update_layout(
        title=dict(text="AI as Cause", font=dict(size=12, color='#94a3b8')),
        showlegend=False
    )
    st.plotly_chart(fig_ai, use_container_width=True)

with col_s3:
    reason_df = df.groupby('reason')['employees_laid_off'].sum().reset_index().sort_values('employees_laid_off', ascending=False).head(6)
    fig_reason = go.Figure(go.Bar(
        x=reason_df['employees_laid_off'], y=reason_df['reason'],
        orientation='h',
        marker_color='#a78bfa', marker_line_width=0
    ))
    fig_reason = apply_dark(fig_reason, height=320)
    fig_reason.update_layout(title=dict(text="Top Layoff Reasons", font=dict(size=12, color='#94a3b8')))
    st.plotly_chart(fig_reason, use_container_width=True)

# ─── SECTION 3: WORKFORCE IMPACT DEPTH ───────────────────────────────────────
st.markdown("<div class='section-header'>03 · Workforce Impact Depth</div>", unsafe_allow_html=True)

col_d1, col_d2 = st.columns([5, 5])

with col_d1:
    # Scatter: Company size vs % cut
    fig_scatter = px.scatter(
        df,
        x='total_employees', y='percentage_workforce',
        size='employees_laid_off', color='ai_related',
        hover_name='company',
        hover_data={'industry': True, 'employees_laid_off': True},
        color_discrete_map={'Yes': '#3b82f6', 'No': '#f87171', 'Partial': '#fbbf24'},
        labels={'total_employees': 'Company Size', 'percentage_workforce': '% Workforce Cut'}
    )
    fig_scatter = apply_dark(fig_scatter, height=320)
    fig_scatter.update_layout(
        title=dict(text="Company Size vs. % Workforce Cut (bubble = headcount)", font=dict(size=12, color='#94a3b8')),
        legend_title_text="AI-Related"
    )
    fig_scatter.update_xaxes(type='log')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_d2:
    # Severance by industry
    sev_df = df.groupby('industry')['severance_weeks'].mean().reset_index().sort_values('severance_weeks', ascending=False)
    fig_sev = go.Figure(go.Bar(
        x=sev_df['industry'], y=sev_df['severance_weeks'],
        marker=dict(
            color=sev_df['severance_weeks'],
            colorscale=[[0, '#1e3a5f'], [1, '#34d399']],
            showscale=False
        )
    ))
    fig_sev = apply_dark(fig_sev, height=320)
    fig_sev.update_layout(
        title=dict(text="Average Severance Weeks by Industry", font=dict(size=12, color='#94a3b8')),
        xaxis_tickangle=-35
    )
    st.plotly_chart(fig_sev, use_container_width=True)

# ─── SECTION 4: DEPARTMENT + GEOGRAPHY ───────────────────────────────────────
st.markdown("<div class='section-header'>04 · Department & Geography</div>", unsafe_allow_html=True)

col_g1, col_g2 = st.columns([5, 5])

with col_g1:
    # Department parsing (comma-separated values)
    dept_series = df['department'].dropna().str.split(',').explode().str.strip()
    dept_df = dept_series.value_counts().reset_index()
    dept_df.columns = ['Department', 'Count']
    dept_df = dept_df.head(10)
    fig_dept = go.Figure(go.Bar(
        x=dept_df['Count'], y=dept_df['Department'],
        orientation='h',
        marker_color='#fbbf24', marker_line_width=0
    ))
    fig_dept = apply_dark(fig_dept, height=320)
    fig_dept.update_layout(title=dict(text="Most Impacted Departments", font=dict(size=12, color='#94a3b8')))
    st.plotly_chart(fig_dept, use_container_width=True)

with col_g2:
    country_df = df.groupby('country')['employees_laid_off'].sum().reset_index().sort_values('employees_laid_off', ascending=False)
    fig_country = go.Figure(go.Bar(
        x=country_df['country'], y=country_df['employees_laid_off'],
        marker=dict(
            color=country_df['employees_laid_off'],
            colorscale=[[0, '#1e3a5f'], [1, '#f87171']],
            showscale=False
        )
    ))
    fig_country = apply_dark(fig_country, height=320)
    fig_country.update_layout(title=dict(text="Layoffs by Country", font=dict(size=12, color='#94a3b8')))
    st.plotly_chart(fig_country, use_container_width=True)

# ─── SECTION 5: COMPANY DRILL-DOWN ───────────────────────────────────────────
st.markdown("<div class='section-header'>05 · Company Intelligence</div>", unsafe_allow_html=True)

search_col, _ = st.columns([4, 6])
with search_col:
    company_query = st.text_input("Search company", placeholder="e.g. Google, Meta, Intel...")

if company_query:
    result = df[df['company'].str.contains(company_query, case=False, na=False)]
    if result.empty:
        st.info("No matching company found in current filter selection.")
    else:
        for _, row in result.iterrows():
            ai_color = "#3b82f6" if row['ai_related'] == 'Yes' else ("#fbbf24" if row['ai_related'] == 'Partial' else "#f87171")
            st.markdown(f"""<div class='company-card'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <span style='font-family:Space Mono,monospace;font-size:1rem;font-weight:700;color:#f1f5f9;'>{row['company']}</span>
                        <span class='tag-chip' style='margin-left:8px;'>{row['industry']}</span>
                        <span class='tag-chip'>{row['country']}</span>
                        <span class='tag-chip' style='color:{ai_color};border-color:{ai_color};'>AI: {row['ai_related']}</span>
                    </div>
                    <div style='font-family:Space Mono,monospace;font-size:1.4rem;font-weight:700;color:#f87171;'>{int(row['employees_laid_off']):,} roles</div>
                </div>
                <div style='margin-top:0.6rem;display:flex;gap:2rem;font-size:0.8rem;color:#64748b;'>
                    <span>📅 {row['date'].strftime('%d %b %Y')}</span>
                    <span>📉 {row['percentage_workforce']}% workforce</span>
                    <span>💼 {row['severance_weeks']} weeks severance</span>
                    <span>🏢 {int(row['total_employees']):,} total employees</span>
                </div>
                <div style='margin-top:0.5rem;font-size:0.8rem;color:#94a3b8;'>
                    <b>Reason:</b> {row['reason']} &nbsp;|&nbsp; <b>Departments:</b> {row['department']}
                </div>
            </div>""", unsafe_allow_html=True)

# ─── SECTION 6: QUARTERLY VIEW ───────────────────────────────────────────────
st.markdown("<div class='section-header'>06 · Quarterly Breakdown</div>", unsafe_allow_html=True)

q_df = df.groupby(['year', 'quarter'])['employees_laid_off'].sum().reset_index()
q_df['label'] = q_df['year'].astype(str) + ' Q' + q_df['quarter'].astype(str)

col_q1, col_q2 = st.columns([6, 4])
with col_q1:
    fig_q = go.Figure(go.Bar(
        x=q_df['label'], y=q_df['employees_laid_off'],
        marker=dict(
            color=q_df['employees_laid_off'],
            colorscale=[[0, '#1e3a5f'], [1, '#3b82f6']],
            showscale=False
        )
    ))
    fig_q = apply_dark(fig_q, height=260)
    fig_q.update_layout(title=dict(text="Total Layoffs per Quarter", font=dict(size=12, color='#94a3b8')))
    st.plotly_chart(fig_q, use_container_width=True)

with col_q2:
    ai_q = df.groupby('ai_related')['employees_laid_off'].agg(['sum', 'count']).reset_index()
    ai_q.columns = ['AI Related', 'Total Roles', 'Events']
    ai_q['Avg per Event'] = (ai_q['Total Roles'] / ai_q['Events']).round(0).astype(int)
    ai_q['Total Roles'] = ai_q['Total Roles'].apply(lambda x: f"{x:,}")
    st.dataframe(
        ai_q,
        use_container_width=True,
        hide_index=True,
        column_config={
            "AI Related": st.column_config.TextColumn("AI Cause"),
            "Total Roles": st.column_config.TextColumn("Total Roles"),
            "Events": st.column_config.NumberColumn("Events"),
            "Avg per Event": st.column_config.NumberColumn("Avg / Event"),
        }
    )

# ─── SECTION 7: RAW DATA ─────────────────────────────────────────────────────
with st.expander("📋 Full Dataset View"):
    display_cols = ['company', 'date', 'industry', 'country', 'employees_laid_off',
                    'percentage_workforce', 'reason', 'department', 'ai_related', 'severance_weeks']
    st.dataframe(
        df[display_cols].sort_values('employees_laid_off', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    csv = df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Export to CSV", csv, "techpulse_filtered.csv", "text/csv")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;font-size:0.72rem;color:#334155;padding:1rem 0;'>
    TechPulse 2026 · Built by Shivani Tomar · Data Systems Analyst<br>
    Dataset covers 35 companies · 2025–2026 · For portfolio and research purposes
</div>
""", unsafe_allow_html=True)
