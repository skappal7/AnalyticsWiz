"""
Data Storyteller Analytics App
Production-ready Streamlit application for generic data analytics
"""

import streamlit as st
import polars as pl
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import COLORS, COLUMN_MAPPING
from utils.pii_redactor import PIIRedactor
from utils.data_processor import DataProcessor
from assets.icons import get_icon, icon_html, section_header, metric_card
from modules.executive_dashboard import render_executive_dashboard
from modules.time_intelligence import render_time_intelligence
from modules.sky_partner_analysis import render_sky_partner_analysis
from modules.regional_deep_dive import render_regional_deep_dive
from modules.root_cause_analysis import render_root_cause_analysis
from modules.recommendations import render_recommendations
from modules.recommendations import render_recommendations
from modules.text_analytics_module import render_text_analytics
from modules.generic_analysis import render_generic_analysis


# Page configuration
st.set_page_config(
    page_title="Data Storyteller",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with muted colors
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables - Professional muted palette */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #64748b;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --border: #e2e8f0;
    }
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1 {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.025em;
    }
    
    h2 {
        font-size: 1.375rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.025em;
        margin-top: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: #334155;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--bg-tertiary);
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.625rem 1.25rem;
        background: transparent;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-primary) !important;
        color: var(--primary) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 0.875rem 1rem !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* File uploader */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        border: 2px dashed #475569;
        border-radius: 8px;
        padding: 1rem;
        background: rgba(255,255,255,0.05);
    }
    
    section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: var(--primary);
        background: rgba(37,99,235,0.1);
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def load_data(uploaded_file) -> pl.DataFrame:
    """Load data from uploaded file."""
    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith('.csv'):
            return pl.read_csv(uploaded_file, infer_schema_length=10000)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            return pl.read_excel(uploaded_file)
        elif filename.endswith('.parquet'):
            return pl.read_parquet(uploaded_file)
        else:
            st.error(f"Unsupported file format: {filename}")
            return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def main():
    """Main application entry point."""
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'pii_redacted' not in st.session_state:
        st.session_state.pii_redacted = False
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    
    # Sidebar
    with st.sidebar:
        # Logo/Title with icon
        st.markdown(f'''
<div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
<div style="display:flex;align-items:center;justify-content:center;width:40px;height:40px;background:linear-gradient(135deg,#2563eb,#7c3aed);border-radius:10px">
{get_icon('sparkles', 22, 'white')}
</div>
<div>
<h3 style="margin:0;font-size:1.125rem;color:#f1f5f9">Data Storyteller</h3>
<p style="margin:0;font-size:0.75rem;color:#94a3b8">Universal Analytics</p>
</div>
</div>
''', unsafe_allow_html=True)
        
        st.divider()
        
        # Analysis Mode Selection
        st.markdown(f'{icon_html("settings", 18, "#94a3b8")} **Configuration**', unsafe_allow_html=True)
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Paramount Analysis", "Analysis for All"],
            help="Select 'Paramount Analysis' for standard dashboard or 'Analysis for All' for custom exploration."
        )
        
        st.divider()
        
        # Upload section
        st.markdown(f'{icon_html("upload", 18, "#94a3b8")} **Data Upload**', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload contact center data",
            type=['csv', 'xlsx', 'parquet'],
            help="Supports CSV, Excel, and Parquet files up to 200MB",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            if st.session_state.filename != uploaded_file.name:
                with st.spinner("Loading..."):
                    df = load_data(uploaded_file)
                    if df is not None:
                        st.session_state.data = df
                        st.session_state.filename = uploaded_file.name
                        st.session_state.pii_redacted = False
                        st.success(f"Loaded {len(df):,} rows")
        
        st.divider()
        
        # Privacy section
        st.markdown(f'{icon_html("shield", 18, "#94a3b8")} **Privacy**', unsafe_allow_html=True)
        
        enable_pii = st.checkbox(
            "Enable PII Redaction",
            value=True,
            help="GDPR-compliant redaction"
        )
        
        if enable_pii and st.session_state.data is not None and not st.session_state.pii_redacted:
            with st.spinner("Redacting..."):
                try:
                    redactor = PIIRedactor()
                    columns = st.session_state.data.columns
                    
                    desc_cols = []
                    if COLUMN_MAPPING['description'] < len(columns):
                        desc_cols.append(columns[COLUMN_MAPPING['description']])
                    if COLUMN_MAPPING['description_translated'] < len(columns):
                        desc_cols.append(columns[COLUMN_MAPPING['description_translated']])
                    
                    if desc_cols:
                        st.session_state.data = redactor.redact_dataframe(
                            st.session_state.data, desc_cols
                        )
                        st.session_state.pii_redacted = True
                        st.success("PII redacted")
                except Exception as e:
                    st.warning(f"Warning: {str(e)}")
        
        st.divider()
        
        # Data summary
        if st.session_state.data is not None:
            st.markdown(f'{icon_html("bar_chart", 18, "#94a3b8")} **Data Summary**', unsafe_allow_html=True)
            
            df_info = st.session_state.data
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", f"{len(df_info):,}")
            with col2:
                st.metric("Cols", len(df_info.columns))
            
            mem_mb = df_info.estimated_size() / (1024 * 1024)
            st.caption(f"Memory: {mem_mb:.1f} MB")
    
    # Main content
    # Header with icon
    st.markdown(f'''
<div style="display:flex;align-items:center;gap:14px;margin-bottom:0.5rem">
<div style="display:flex;align-items:center;justify-content:center;width:48px;height:48px;background:linear-gradient(135deg,#2563eb,#7c3aed);border-radius:12px;box-shadow:0 4px 12px rgba(37,99,235,0.3)">
{get_icon('chart', 26, 'white')}
</div>
<div>
<h1 style="margin:0;font-size:1.75rem;font-weight:700;color:#1e293b">Data Storyteller</h1>
<p style="margin:0;font-size:0.875rem;color:#64748b">Universal Data Analytics Platform</p>
</div>
</div>
''', unsafe_allow_html=True)
    
    # No data state
    if st.session_state.data is None:
        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
        
        st.info("**Getting Started** — Upload a CSV, Excel, or Parquet file using the sidebar to begin analysis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'''
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.75rem">
{get_icon('file_text', 20, '#2563eb')}
<span style="font-weight:600;color:#1e293b">Expected Data Structure</span>
</div>
<table style="width:100%;font-size:0.875rem;color:#475569">
<tr><td style="padding:4px 0;border-bottom:1px solid #e2e8f0"><b>Col A</b></td><td>Queue Name</td></tr>
<tr><td style="padding:4px 0;border-bottom:1px solid #e2e8f0"><b>Col J</b></td><td>Date/Time</td></tr>
<tr><td style="padding:4px 0;border-bottom:1px solid #e2e8f0"><b>Col M</b></td><td>Description</td></tr>
<tr><td style="padding:4px 0;border-bottom:1px solid #e2e8f0"><b>Col S</b></td><td>Partner</td></tr>
<tr><td style="padding:4px 0;border-bottom:1px solid #e2e8f0"><b>Col U</b></td><td>Country</td></tr>
<tr><td style="padding:4px 0"><b>Col V</b></td><td>Translation</td></tr>
</table>
</div>
''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.75rem">
{get_icon('zap', 20, '#2563eb')}
<span style="font-weight:600;color:#1e293b">Features</span>
</div>
<ul style="margin:0;padding-left:1.25rem;font-size:0.875rem;color:#475569;line-height:1.8">
<li>GDPR-compliant PII redaction</li>
<li>7 analytics modules</li>
<li>Automated regional insights</li>
<li>Optimized for 50K+ rows</li>
<li>Executive-ready outputs</li>
</ul>
</div>
''', unsafe_allow_html=True)
        return
    
    df = st.session_state.data
    
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    
    # KPI row with icons
    col1, col2, col3, col4 = st.columns(4)
    
    if analysis_mode == "Paramount Analysis":
        processor = DataProcessor(df)
        stats = processor.get_summary_stats()
        
        with col1:
            st.markdown(metric_card(f"{stats['total_rows']:,}", "Total Cases", "users"), unsafe_allow_html=True)
        
        with col2:
            country_col = processor.get_column('country')
            markets = df[country_col].n_unique() if country_col else 0
            st.markdown(metric_card(str(markets), "Markets", "globe"), unsafe_allow_html=True)
        
        with col3:
            sky_pct = processor.get_sky_partner_percentage()
            st.markdown(metric_card(f"{sky_pct:.1f}%", "Sky Partner", "partner"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(metric_card(f"{stats['memory_usage_mb']:.1f} MB", "Memory", "layers"), unsafe_allow_html=True)
            
    else:
        # Generic KPIs for Analysis for All
        with col1:
             st.markdown(metric_card(f"{len(df):,}", "Total Rows", "users"), unsafe_allow_html=True)
        
        with col2:
             st.markdown(metric_card(str(len(df.columns)), "Columns", "layout"), unsafe_allow_html=True)
             
        with col3:
             # Count numeric columns
             num_cols = len([c for c in df.columns if df[c].dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]])
             st.markdown(metric_card(str(num_cols), "Numeric Vars", "hash"), unsafe_allow_html=True)
             
        with col4:
             mem_mb = df.estimated_size() / (1024 * 1024)
             st.markdown(metric_card(f"{mem_mb:.1f} MB", "Memory", "zap"), unsafe_allow_html=True)
    
    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    
    # Tabs with icons
    if analysis_mode == "Paramount Analysis":
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "Executive",
            "Trends", 
            "Sky Partners",
            "Regional",
            "Root Cause",
            "Actions",
            "Text Analysis"
        ])
        
        config = {}
        
        with tab1:
            try:
                render_executive_dashboard(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab2:
            try:
                render_time_intelligence(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab3:
            try:
                render_sky_partner_analysis(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab4:
            try:
                render_regional_deep_dive(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab5:
            try:
                render_root_cause_analysis(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab6:
            try:
                render_recommendations(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab7:
            try:
                render_text_analytics(df, config)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
    else:
        # Analysis for All
        try:
            render_generic_analysis(df)
        except Exception as e:
            st.error(f"Error in Generic Analysis: {str(e)}")


if __name__ == "__main__":
    main()
