"""
Module 1: Executive Dashboard
High-level KPIs and strategic insights with visual icons
"""

import streamlit as st
import polars as pl
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS
from utils.visualizations import ChartBuilder
from utils.data_processor import DataProcessor
from assets.icons import section_header, metric_card, info_card, success_card, icon_text


def render_executive_dashboard(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Executive Dashboard module."""
    
    # Section header with icon
    st.markdown(section_header("Executive Dashboard", "dashboard", "High-level KPIs and strategic insights"), unsafe_allow_html=True)
    
    processor = DataProcessor(df)
    stats = processor.get_summary_stats()
    
    # Build KPI metrics
    try:
        total_cases = stats['total_rows']
        
        # Unique markets
        country_col = processor.get_column('country')
        unique_markets = df[country_col].n_unique() if country_col and country_col in df.columns else 0
        
        # Sky partner percentage
        sky_pct = processor.get_sky_partner_percentage()
        sky_count = processor.get_sky_partner_count()
        
        # Top country
        if country_col and country_col in df.columns:
            top_country_df = processor.get_top_n(country_col, 1)
            top_country = str(top_country_df[country_col][0]) if len(top_country_df) > 0 else 'N/A'
            top_country_count = int(top_country_df['count'][0]) if len(top_country_df) > 0 else 0
        else:
            top_country = 'N/A'
            top_country_count = 0
        
        # Top issue
        subcat_col = processor.get_column('subcategory')
        cat_col = processor.get_column('category')
        issue_col = subcat_col if subcat_col else cat_col
        
        if issue_col and issue_col in df.columns:
            top_issue_df = processor.get_top_n(issue_col, 1)
            top_issue = str(top_issue_df[issue_col][0]) if len(top_issue_df) > 0 else 'N/A'
            top_issue_count = int(top_issue_df['count'][0]) if len(top_issue_df) > 0 else 0
            top_issue_pct = round(top_issue_count / total_cases * 100, 1) if total_cases > 0 else 0
        else:
            top_issue = 'N/A'
            top_issue_count = 0
            top_issue_pct = 0
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(metric_card(f"{total_cases:,}", "Total Cases", "users"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(str(unique_markets), "Markets", "globe"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(f"{sky_pct:.1f}%", "Sky Partner", "partner"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card(f"{top_issue_pct:.1f}%", "Top Issue Share", "target"), unsafe_allow_html=True)
    with col5:
        st.markdown(metric_card(top_country, "Top Market", "map"), unsafe_allow_html=True)
    
    st.divider()
    
    # Charts Row
    chart_col1, chart_col2 = st.columns(2)
    charts = ChartBuilder(height=380)
    
    with chart_col1:
        st.markdown(icon_text("bar_chart", "Top 10 Countries", 18, "#2563eb"), unsafe_allow_html=True)
        if country_col and country_col in df.columns:
            top_countries = processor.get_top_n(country_col, 10)
            if len(top_countries) > 0:
                fig = charts.create_bar_chart(
                    top_countries, country_col, 'count',
                    title='',
                    horizontal=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Country column not found")
    
    with chart_col2:
        st.markdown(icon_text("pie_chart", "Category Distribution", 18, "#2563eb"), unsafe_allow_html=True)
        if cat_col and cat_col in df.columns:
            cat_dist = processor.get_distribution(cat_col).head(8)
            if len(cat_dist) > 0:
                fig = charts.create_pie_chart(
                    cat_dist, cat_col, 'count',
                    title=''
                )
                st.plotly_chart(fig, use_container_width=True)
        elif issue_col and issue_col in df.columns:
            issue_dist = processor.get_distribution(issue_col).head(8)
            if len(issue_dist) > 0:
                fig = charts.create_pie_chart(
                    issue_dist, issue_col, 'count',
                    title=''
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category column not found")
    
    st.divider()
    
    # Executive Summary with proper icon cards
    st.markdown(icon_text("sparkles", "Executive Summary", 20, "#2563eb"), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(info_card(
            f"Top Issue: {top_issue}",
            f"Accounts for {top_issue_pct:.1f}% of total volume ({top_issue_count:,} cases). This is the primary driver of contact center load.",
            "target", "blue"
        ), unsafe_allow_html=True)
        
        st.markdown(info_card(
            f"Sky Partner Impact: {sky_pct:.1f}%",
            f"{sky_count:,} cases involve Sky partner integrations. These represent a significant escalation pathway.",
            "partner", "blue"
        ), unsafe_allow_html=True)
    
    with col2:
        top_country_pct = round(top_country_count / total_cases * 100, 1) if total_cases > 0 else 0
        st.markdown(info_card(
            f"Market Concentration: {top_country}",
            f"Leads with {top_country_count:,} cases ({top_country_pct}% of global). Consider market-specific interventions.",
            "globe", "blue"
        ), unsafe_allow_html=True)
        
        reduction_potential = int(top_issue_pct * 0.7) if top_issue_pct > 0 else 0
        st.markdown(success_card(
            "Strategic Recommendation",
            f'Prioritize "{top_issue}" — addressing this single issue could reduce overall contact volume by up to {reduction_potential}%.'
        ), unsafe_allow_html=True)
