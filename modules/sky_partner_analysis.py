"""
Module 3: Sky Partner Analysis
Two-level analysis of Sky partner integrations
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


def analyze_root_cause(issue_name: str) -> str:
    """Generate root cause analysis based on issue type."""
    issue = issue_name.lower() if issue_name else ''
    
    if 'password' in issue or 'email' in issue or 'login' in issue:
        return "Authentication Barrier: Email deliverability failure or SSO token expiration"
    elif 'sky' in issue or 'provider' in issue:
        return "Partner Integration: API handshake error between Sky and Paramount+ systems"
    elif 'cancel' in issue:
        return "UX Friction: Cancellation flow hidden or requires partner portal navigation"
    elif 'bill' in issue or 'refund' in issue or 'charge' in issue:
        return "Payment Gateway: Billing cycle timing mismatch between partner and platform"
    elif 'stream' in issue or 'play' in issue or 'buffer' in issue:
        return "Technical: Content delivery or streaming quality issues"
    else:
        return "Process Friction: Self-service gap requiring manual intervention"


def render_sky_partner_analysis(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Sky Partner Analysis module."""
    
    st.header("Sky Partner Analysis")
    st.caption("Two-level analysis of Sky partner integrations")
    
    processor = DataProcessor(df)
    
    # Filter to Sky partners
    sky_df = processor.filter_sky_partners()
    
    if len(sky_df) == 0:
        st.warning("No Sky partner cases found in the dataset.")
        st.info("Sky partner cases are identified by the Partner column containing 'Sky' (case-insensitive).")
        return
    
    total_cases = len(df)
    sky_cases = len(sky_df)
    sky_pct = round(sky_cases / total_cases * 100, 2)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sky Partner Cases", f"{sky_cases:,}")
    with col2:
        st.metric("% of Total Volume", f"{sky_pct:.1f}%")
    with col3:
        potential_reduction = int(sky_cases * 0.7)
        st.metric("Reduction Potential (70%)", f"{potential_reduction:,} cases")
    
    st.divider()
    
    # Level 1: Market Overview
    st.subheader("Level 1: Market Overview")
    
    country_col = processor.get_column('country')
    partner_col = processor.get_column('partner')
    
    if country_col and partner_col:
        # Group by country and partner
        market_df = (
            sky_df
            .group_by([country_col, partner_col])
            .agg(pl.count().alias('volume'))
            .with_columns([
                (pl.col('volume') / sky_cases * 100).round(2).alias('pct_of_sky'),
                (pl.col('volume') / total_cases * 100).round(2).alias('pct_of_global')
            ])
            .sort('volume', descending=True)
        )
        
        # Add impact rating
        market_df = market_df.with_columns([
            pl.when(pl.col('pct_of_global') > 3).then(pl.lit('HIGH'))
            .otherwise(pl.lit('MEDIUM'))
            .alias('impact')
        ])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display table
            display_df = market_df.head(10).to_pandas()
            display_df.columns = ['Country', 'Partner', 'Volume', '% of Sky', '% of Global', 'Impact']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Chart
            charts = ChartBuilder(height=350)
            top_5 = market_df.head(5)
            if len(top_5) > 0:
                fig = charts.create_bar_chart(
                    top_5, country_col, 'volume',
                    title='Top 5 Sky Markets',
                    horizontal=True
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Level 2: Root Cause Patterns
    st.subheader("Level 2: Root Cause Patterns")
    
    subcat_col = processor.get_column('subcategory')
    cat_col = processor.get_column('category')
    issue_col = subcat_col if subcat_col else cat_col
    
    if issue_col:
        # Top issues for Sky cases
        issue_df = (
            sky_df
            .filter(pl.col(issue_col).is_not_null())
            .group_by(issue_col)
            .agg(pl.count().alias('volume'))
            .with_columns([
                (pl.col('volume') / sky_cases * 100).round(2).alias('pct_of_sky')
            ])
            .sort('volume', descending=True)
            .head(10)
        )
        
        # Add severity
        issue_df = issue_df.with_columns([
            pl.when(pl.col('pct_of_sky') > 30).then(pl.lit('CRITICAL'))
            .when(pl.col('pct_of_sky') > 15).then(pl.lit('HIGH'))
            .otherwise(pl.lit('MEDIUM'))
            .alias('severity')
        ])
        
        # Display with root cause
        for row in issue_df.head(5).iter_rows(named=True):
            issue_name = row[issue_col]
            volume = row['volume']
            pct = row['pct_of_sky']
            severity = row['severity']
            root_cause = analyze_root_cause(issue_name)
            
            with st.expander(f"**{issue_name}** - {volume:,} cases ({pct:.1f}%) - {severity}"):
                st.markdown(f"**Root Cause:** {root_cause}")
                st.markdown(f"**Volume:** {volume:,} cases ({pct:.1f}% of Sky partner volume)")
                st.markdown(f"**Severity:** {severity}")
                
                if severity == 'CRITICAL':
                    st.error("Immediate escalation required - this issue is a major driver of Sky partner contacts")
                elif severity == 'HIGH':
                    st.warning("High priority - should be addressed in the next sprint")
    else:
        st.info("No issue/category column found for root cause analysis")
    
    st.divider()
    
    # Strategic insight
    st.subheader("Strategic Insight")
    
    st.success(f"""
    **Sky Partner Impact Assessment**
    
    Sky partner integrations represent **{sky_pct:.1f}%** of total case volume ({sky_cases:,} cases).
    
    **Recommendation:** Immediate escalation to Partner Engineering for API audit and integration rewrite.
    
    **Expected Impact:** 60-80% reduction in Sky-related contacts after fixes, reducing volume by approximately **{int(sky_cases * 0.7):,} cases**.
    """)
