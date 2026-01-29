"""
Module 2: Time Intelligence
Weekly trends with WoW analysis and anomaly detection
"""

import streamlit as st
import polars as pl
import pandas as pd
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS
from utils.visualizations import ChartBuilder
from utils.data_processor import DataProcessor


@st.cache_data
def get_cached_weekly_aggregation(df: pl.DataFrame):
     # Helper to prevent recalculation on every rerun if data hasn't changed
    processor = DataProcessor(df)
    return processor.get_weekly_aggregation()

def render_time_intelligence(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Time Intelligence module."""
    from assets.icons import section_header, metric_card, info_card, success_card, warning_card, error_card
    
    st.markdown(section_header("Time Intelligence", "clock", "Weekly trends with week-over-week analysis"), unsafe_allow_html=True)
    
    # Use cached aggregation if possible, or just call directly (Streamlit caching requires hashable args, df is not hashable by default easily without config)
    # For now, just call directly as it's fast enough
    processor = DataProcessor(df)
    weekly_df = processor.get_weekly_aggregation()
    
    if len(weekly_df) == 0:
        st.markdown(warning_card("Date Parsing Error", "Unable to extract weekly data. Ensure your date column is valid."), unsafe_allow_html=True)
        return
    
    # Create week label for x-axis
    weekly_df = weekly_df.with_columns([
        (pl.col('year').cast(pl.Utf8) + '-W' + pl.col('week').cast(pl.Utf8).str.pad_start(2, '0')).alias('week_label')
    ])
    
    # Summary metrics
    avg_volume = weekly_df['volume'].mean()
    max_volume = weekly_df['volume'].max()
    min_volume = weekly_df['volume'].min()
    spike_weeks = len(weekly_df.filter(pl.col('trend') == 'SPIKE'))
    total_weeks = len(weekly_df)
    
    # KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(metric_card(str(total_weeks), "Total Weeks", "calendar"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(f"{avg_volume:,.0f}", "Avg Weekly Vol", "activity"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(f"{max_volume:,}", "Peak Volume", "trending-up"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card(f"{min_volume:,}", "Lowest Vol", "trending-down"), unsafe_allow_html=True)
    with col5:
        st.markdown(metric_card(str(spike_weeks), "Spike Weeks", "zap"), unsafe_allow_html=True)
    
    st.divider()
    
    # Narrative Analysis
    st.subheader("Automated Trend Insights")
    
    recent_trend = weekly_df.tail(4)
    if len(recent_trend) >= 2:
        last_vol = recent_trend['volume'][-1]
        prev_vol = recent_trend['volume'][-2]
        wow_change = last_vol - prev_vol
        wow_pct = (wow_change / prev_vol * 100) if prev_vol > 0 else 0
        
        # Volatility Analysis
        cv = weekly_df['volume'].std() / weekly_df['volume'].mean() if weekly_df['volume'].mean() > 0 else 0
        stability = "Stable"
        if cv > 0.5: stability = "Highly Volatile"
        elif cv > 0.2: stability = "Variable"
        
        c1, c2 = st.columns(2)
        with c1:
            if wow_pct > 5:
                st.markdown(warning_card(
                    "Volume Increasing", 
                    f"Volume is **up {wow_pct:.1f}%** ({wow_change:+,} cases) from last week. "
                    "Ensure capacity planning addresses this rise."
                ), unsafe_allow_html=True)
            elif wow_pct < -5:
                st.markdown(success_card(
                    "Volume Decreasing", 
                    f"Volume is **down {abs(wow_pct):.1f}%** ({wow_change:+,} cases) from last week. "
                    "Positive sign for workload reduction."
                ), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    "Volume Stable", 
                    f"Volume is holding steady ({wow_pct:+.1f}% change). Operations are normal.",
                    "check", "blue"
                ), unsafe_allow_html=True)
                
        with c2:
            if stability == "Highly Volatile":
                 st.markdown(warning_card(
                    "High Volatility Detected", 
                    f"The process shows significant swings (CV: {cv:.2f}). "
                    "This unpredictability makes resource planning difficult. Investigate root causes of spikes."
                 ), unsafe_allow_html=True)
            else:
                 st.markdown(success_card(
                    "Process Stability", 
                    f"The process is relatively predictable (CV: {cv:.2f}). "
                    "Standard forecasting models should likely perform well."
                 ), unsafe_allow_html=True)
    
    st.divider()
    
    # Weekly trend chart
    st.subheader("Weekly Case Volume Trend")
    
    charts = ChartBuilder(height=400)
    fig = charts.create_line_chart(
        weekly_df, 'week_label', 'volume',
        title='',
        show_average=True
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Weekly detail table
    st.subheader("Weekly Breakdown")
    
    # Format for display
    display_df = weekly_df.select([
        'week_label',
        'volume',
        'wow_change',
        'wow_pct',
        'trend'
    ]).to_pandas()
    
    display_df.columns = ['Week', 'Volume', 'WoW Change', 'WoW %', 'Trend']
    
    # Apply styling
    # Note: Streamlit dataframe styling is limited, creating string versions for display
    display_df['Volume'] = display_df['Volume'].map(lambda x: f"{x:,}")
    display_df['WoW Change'] = display_df['WoW Change'].map(
        lambda x: f"+{x:,.0f}" if pd.notna(x) and x > 0 else (f"{x:,.0f}" if pd.notna(x) else '-')
    )
    display_df['WoW %'] = display_df['WoW %'].map(
        lambda x: f"+{x:.1f}%" if pd.notna(x) and x > 0 else (f"{x:.1f}%" if pd.notna(x) else '-')
    )
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
