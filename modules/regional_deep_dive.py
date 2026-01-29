"""
Module 4: Regional Deep Dive
Market-by-market detailed analysis
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


def get_recommendation(top_issue: str, sky_pct: float, country: str) -> str:
    """Generate recommendation based on issue and context."""
    issue = top_issue.lower() if top_issue else ''
    
    if 'password' in issue or 'login' in issue or 'email' in issue:
        return f"Deploy SMS-based password reset for {country}. Extend token validity to 24hrs."
    elif 'cancel' in issue:
        return f"Redesign cancellation UX for {country}. Add prominent 'Manage Subscription' button."
    elif 'bill' in issue or 'charge' in issue or 'refund' in issue:
        return f"Implement proactive billing notifications 48hrs before charge for {country}."
    elif sky_pct > 5:
        return f"Escalate Sky API integration fix to Partner Engineering for {country}."
    else:
        return f"Create localized FAQ targeting top 3 issues for {country}."


def render_regional_deep_dive(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Regional Deep Dive module."""
    
    st.header("Regional Deep Dive")
    st.caption("Market-by-market detailed analysis")
    
    processor = DataProcessor(df)
    total_cases = len(df)
    
    country_col = processor.get_column('country')
    subcat_col = processor.get_column('subcategory')
    cat_col = processor.get_column('category')
    partner_col = processor.get_column('partner')
    issue_col = subcat_col if subcat_col else cat_col
    
    if not country_col:
        st.error("Country column not found in dataset.")
        st.info("Ensure Column U contains country data.")
        return
    
    # Get top countries
    top_countries = processor.get_top_n(country_col, 10)
    
    if len(top_countries) == 0:
        st.warning("No country data available.")
        return
    
    # Calculate global average
    unique_countries = df[country_col].n_unique()
    avg_per_country = total_cases / unique_countries if unique_countries > 0 else 0
    
    # Country selector
    country_list = top_countries[country_col].to_list()
    selected_country = st.selectbox("Select Market", country_list, key="regional_country")
    
    # Filter to selected country
    country_df = df.filter(pl.col(country_col) == selected_country)
    country_volume = len(country_df)
    country_pct = round(country_volume / total_cases * 100, 2)
    
    # Calculate vs global average
    vs_avg = round((country_volume / avg_per_country - 1) * 100, 1) if avg_per_country > 0 else 0
    vs_avg_label = f"+{vs_avg}% above avg" if vs_avg > 0 else f"{abs(vs_avg)}% below avg"
    
    # Sky presence
    sky_count = 0
    if partner_col and partner_col in country_df.columns:
        sky_count = len(country_df.filter(
            pl.col(partner_col).is_not_null() &
            pl.col(partner_col).str.to_lowercase().str.contains('sky')
        ))
    sky_pct = round(sky_count / country_volume * 100, 2) if country_volume > 0 else 0

    
    st.divider()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{selected_country} Volume", f"{country_volume:,}")
    with col2:
        st.metric("% of Global", f"{country_pct:.1f}%")
    with col3:
        st.metric("vs Global Avg", vs_avg_label)
    with col4:
        st.metric("Sky Impact", f"{sky_pct:.1f}%")
    
    st.divider()
    
    # Top issues table
    st.subheader("Top 5 Issues")
    
    top_issue = 'Unknown'
    top_issue_pct = 0
    
    if issue_col:
        issues = (
            country_df
            .filter(pl.col(issue_col).is_not_null())
            .group_by(issue_col)
            .agg(pl.count().alias('volume'))
            .with_columns([
                (pl.col('volume') / country_volume * 100).round(2).alias('percentage')
            ])
            .sort('volume', descending=True)
            .head(5)
        )
        
        if len(issues) > 0:
            display_issues = issues.to_pandas()
            display_issues.columns = ['Issue', 'Volume', '% of Country']
            st.dataframe(display_issues, use_container_width=True, hide_index=True)
            
            top_issue = issues[issue_col][0]
            top_issue_pct = issues['percentage'][0]
        else:
            st.info("No issue data available for this country")
    else:
        st.info("No issue/category column found")
    
    st.divider()
    
    # Analysis
    st.subheader("Market Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if vs_avg > 20:
            st.error(f"""
            **High Volume Market**
            
            {selected_country} is **{vs_avg:.0f}% above** the global average per market.
            This market requires immediate attention and targeted interventions.
            """)
        elif vs_avg > 0:
            st.warning(f"""
            **Above Average Volume**
            
            {selected_country} is **{vs_avg:.0f}% above** the global average.
            Consider market-specific optimizations.
            """)
        else:
            st.success(f"""
            **Below Average Volume**
            
            {selected_country} is **{abs(vs_avg):.0f}% below** the global average.
            This market is performing well relative to others.
            """)
    
    with col2:
        st.info(f"""
        **Dominant Issue:** {top_issue}
        
        Concentration: **{top_issue_pct:.1f}%** of {selected_country} volume
        
        {"This concentration is significantly above typical levels." if top_issue_pct > 20 else "This is in line with global patterns."}
        """)
    
    st.divider()
    
    # Recommendation
    st.subheader("Recommendation")
    
    rec = get_recommendation(top_issue, sky_pct, selected_country)
    deflection_est = int(country_volume * 0.15)
    
    st.success(f"""
    **{rec}**
    
    Estimated case reduction: **{deflection_est:,} cases** (15% deflection rate)
    """)
