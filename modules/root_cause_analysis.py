"""
Module 5: Root Cause Analysis
Issue severity classification and prioritization
"""

import streamlit as st
import polars as pl
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, SEVERITY_THRESHOLDS
from utils.visualizations import ChartBuilder
from utils.data_processor import DataProcessor


def get_root_cause_detail(issue_name: str) -> Dict[str, Any]:
    """Get detailed root cause analysis for an issue."""
    issue = issue_name.lower() if issue_name else ''
    
    if 'password' in issue or 'login' in issue or 'email' in issue:
        return {
            'root_cause': 'Authentication Barrier',
            'factors': [
                'Email deliverability issues with major providers',
                'SSO token expiration too short (15 min)',
                'Password reset link blocked by spam filters',
                'No SMS fallback option available'
            ],
            'fix': 'Implement SMS-based 2FA with 24hr token validity',
            'reduction': '70-80%'
        }
    elif 'cancel' in issue or 'unsubscribe' in issue:
        return {
            'root_cause': 'UX Friction',
            'factors': [
                'Cancel button hidden in account settings',
                'Multiple confirmation screens required',
                'Lack of pause subscription option',
                'No clear retention offer presented'
            ],
            'fix': 'Redesign cancellation flow with 1-click save options',
            'reduction': '40-50%'
        }
    elif 'bill' in issue or 'charge' in issue or 'refund' in issue:
        return {
            'root_cause': 'Payment Gateway Issue',
            'factors': [
                'Billing cycle timing confusion',
                'No proactive charge notifications',
                'Trial end date unclear to users',
                'Refund policy not visible in app'
            ],
            'fix': 'Send billing reminders 48hrs before charge',
            'reduction': '50-60%'
        }
    elif 'sky' in issue or 'partner' in issue or 'provider' in issue:
        return {
            'root_cause': 'Partner Integration Failure',
            'factors': [
                'API handshake errors between systems',
                'Account linking failures',
                'Subscription status sync delays',
                'Partner portal UX limitations'
            ],
            'fix': 'Escalate to Partner Engineering for API audit',
            'reduction': '60-70%'
        }
    else:
        return {
            'root_cause': 'Self-Service Gap',
            'factors': [
                'FAQ does not cover this issue',
                'Chatbot unable to resolve',
                'Help articles outdated',
                'No video tutorials available'
            ],
            'fix': 'Expand self-service content for this issue category',
            'reduction': '30-40%'
        }


def render_root_cause_analysis(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Root Cause Analysis module."""
    
    st.header("Root Cause Analysis")
    st.caption("Issue severity classification and prioritization")
    
    processor = DataProcessor(df)
    total_cases = len(df)
    
    subcat_col = processor.get_column('subcategory')
    cat_col = processor.get_column('category')
    issue_col = subcat_col if subcat_col else cat_col
    
    if not issue_col:
        st.warning("No category or sub-category column found in dataset.")
        st.info("Ensure your data has a Category or Sub-Category column.")
        return
    
    # Get issue distribution with severity
    issues = (
        df
        .filter(pl.col(issue_col).is_not_null())
        .group_by(issue_col)
        .agg(pl.count().alias('volume'))
        .with_columns([
            (pl.col('volume') / total_cases * 100).round(2).alias('pct_impact')
        ])
        .sort('volume', descending=True)
    )
    
    # Add severity classification
    issues = issues.with_columns([
        pl.when(pl.col('pct_impact') > SEVERITY_THRESHOLDS['critical']).then(pl.lit('CRITICAL'))
        .when(pl.col('pct_impact') > SEVERITY_THRESHOLDS['high']).then(pl.lit('HIGH'))
        .when(pl.col('pct_impact') > SEVERITY_THRESHOLDS['medium']).then(pl.lit('MEDIUM'))
        .otherwise(pl.lit('LOW'))
        .alias('severity')
    ])
    
    # Summary metrics
    critical_count = len(issues.filter(pl.col('severity') == 'CRITICAL'))
    high_count = len(issues.filter(pl.col('severity') == 'HIGH'))
    top_3_volume = issues.head(3)['volume'].sum()
    top_3_pct = round(top_3_volume / total_cases * 100, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Critical Issues", critical_count)
    with col2:
        st.metric("High Priority Issues", high_count)
    with col3:
        st.metric("Top 3 Issues Volume", f"{top_3_volume:,}")
    with col4:
        st.metric("Top 3 Concentration", f"{top_3_pct}%")
    
    st.divider()
    
    # Issue table
    st.subheader("Issue Prioritization Matrix")
    
    display_df = issues.head(15).to_pandas()
    display_df.columns = ['Issue', 'Volume', '% Impact', 'Severity']
    display_df['Volume'] = display_df['Volume'].map(lambda x: f"{x:,}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Deep dive for top 3
    st.subheader("Root Cause Deep Dive")
    st.caption("Detailed analysis of top 3 issues with recommended fixes")
    
    for idx, row in enumerate(issues.head(3).iter_rows(named=True)):
        issue_name = row[issue_col]
        volume = row['volume']
        pct = row['pct_impact']
        severity = row['severity']
        
        detail = get_root_cause_detail(issue_name)
        
        with st.expander(f"**#{idx+1} {issue_name}** - {volume:,} cases ({pct:.1f}%) - {severity}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Root Cause:** {detail['root_cause']}")
                st.markdown("**Contributing Factors:**")
                for factor in detail['factors']:
                    st.markdown(f"- {factor}")
            
            with col2:
                st.markdown(f"**Recommended Fix:** {detail['fix']}")
                st.markdown(f"**Expected Reduction:** {detail['reduction']}")
                
                potential_reduction = int(volume * 0.7)
                st.metric("Potential Case Reduction", f"{potential_reduction:,} cases")
            
            if severity == 'CRITICAL':
                st.error("This is a CRITICAL priority issue requiring immediate attention.")
            elif severity == 'HIGH':
                st.warning("This is a HIGH priority issue to be addressed in the next sprint.")
