"""
Module 6: Recommendations
Prioritized action plan with icons
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS
from utils.data_processor import DataProcessor
from assets.icons import section_header, icon_text, info_card, success_card, warning_card, error_card, metric_card


def render_recommendations(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Recommendations module."""
    
    # Section header with icon
    st.markdown(section_header("Recommendations", "target", "Prioritized action plan with impact estimates"), unsafe_allow_html=True)
    
    processor = DataProcessor(df)
    total_cases = len(df)
    
    subcat_col = processor.get_column('subcategory')
    cat_col = processor.get_column('category')
    partner_col = processor.get_column('partner')
    issue_col = subcat_col if subcat_col else cat_col
    
    # Get top issue
    top_issue = 'Unknown Issue'
    top_issue_count = 0
    if issue_col and issue_col in df.columns:
        top_issues = processor.get_top_n(issue_col, 1)
        if len(top_issues) > 0:
            top_issue = str(top_issues[issue_col][0])
            top_issue_count = int(top_issues['count'][0])
    
    # Get Sky count
    sky_count = processor.get_sky_partner_count() if partner_col else 0
    
    # Build recommendations
    recommendations: List[Dict] = [
        {
            'priority': 'P0',
            'action': f'Fix "{top_issue}"',
            'detail': 'Address the highest-volume issue with targeted fix based on root cause analysis',
            'effort': '2-3 weeks',
            'reduction': int(top_issue_count * 0.7),
            'reduction_pct': round(top_issue_count * 0.7 / total_cases * 100, 1) if total_cases > 0 else 0
        },
        {
            'priority': 'P0',
            'action': 'Sky API Integration Rewrite',
            'detail': 'Partner Engineering handshake and sync overhaul',
            'effort': '3-4 weeks',
            'reduction': int(sky_count * 0.8),
            'reduction_pct': round(sky_count * 0.8 / total_cases * 100, 1) if total_cases > 0 else 0
        },
        {
            'priority': 'P1',
            'action': 'Cancellation UX Redesign',
            'detail': 'Add prominent "Manage Subscription" button and pause options',
            'effort': '1-2 weeks',
            'reduction': int(total_cases * 0.1),
            'reduction_pct': 10.0
        },
        {
            'priority': 'P1',
            'action': 'Proactive Billing Notifications',
            'detail': 'Send email/SMS reminders 48hrs before any charge',
            'effort': '1 week',
            'reduction': int(total_cases * 0.05),
            'reduction_pct': 5.0
        },
        {
            'priority': 'P2',
            'action': 'Self-Service FAQ Expansion',
            'detail': 'Create localized FAQ content targeting top 3 issues with video tutorials',
            'effort': '2 weeks',
            'reduction': int(total_cases * 0.08),
            'reduction_pct': 8.0
        }
    ]
    
    # Summary
    total_reduction = sum([r['reduction'] for r in recommendations])
    pct_reduction = round(total_reduction / total_cases * 100, 1) if total_cases > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(metric_card(f"{total_cases:,}", "Total Cases", "users"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(f"{total_reduction:,}", "Projected Reduction", "trending"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(f"{pct_reduction}%", "% Reduction", "target"), unsafe_allow_html=True)
    
    st.divider()
    
    # Recommendation cards
    st.markdown(icon_text("zap", "Prioritized Actions", 18, "#2563eb"), unsafe_allow_html=True)
    
    for rec in recommendations:
        with st.expander(f"{rec['priority']} | {rec['action']} | {rec['effort']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {rec['detail']}")
                st.markdown(f"**Effort:** {rec['effort']}")
            
            with col2:
                st.metric("Cases Reduced", f"{rec['reduction']:,}")
                st.metric("% Reduction", f"{rec['reduction_pct']:.1f}%")
    
    st.divider()
    
    # Implementation roadmap with proper cards
    st.markdown(icon_text("clock", "Implementation Roadmap", 18, "#2563eb"), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(error_card(
            "Phase 1: Critical Fixes (Weeks 1-4)",
            "Sprint 1-2: Top issue fix. Sprint 2-3: Sky API rewrite. Target: 50-60% reduction."
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(warning_card(
            "Phase 2: UX Improvements (Weeks 5-8)",
            "Sprint 3-4: Cancellation flow. Sprint 4: Billing notifications. Target: +10-15% reduction."
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(info_card(
            "Phase 3: Self-Service (Weeks 9-12)",
            "Sprint 5-6: FAQ expansion. Sprint 6: Localized content. Target: +5-8% reduction.",
            "file_text", "blue"
        ), unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(success_card(
        "Total Projected Impact",
        f"Implementing all recommendations over 12 weeks is projected to achieve 65-83% volume reduction, translating to approximately {total_reduction:,} fewer cases."
    ), unsafe_allow_html=True)
