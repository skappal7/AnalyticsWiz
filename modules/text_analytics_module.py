"""
Module 7: Text Analytics
Rich regional insights with narrative analysis
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS
from utils.visualizations import ChartBuilder
from utils.data_processor import DataProcessor
from utils.text_analytics import TextAnalyzer


# Theme definitions with detailed narratives
THEME_NARRATIVES = {
    'Cancellation': {
        'title': 'Cancellation / unsubscribe difficulties',
        'description': 'Customers attempting to cancel subscriptions or free trials, difficulty finding or completing the cancellation process, broken web/app flows, and frequent requests for support to cancel on their behalf.',
        'keywords': ['cancel', 'unsubscribe', 'terminate', 'stop subscription', 'end subscription', 'free trial', 'how to cancel', 'cannot cancel']
    },
    'Billing': {
        'title': 'Billing issues & refunds',
        'description': 'Unexpected charges, charges after cancellation, disputed renewals, refund requests, double billing, and complaints about being charged without actively using the service.',
        'keywords': ['refund', 'charged', 'unexpected charge', 'double bill', 'charge after cancel', 'billing', 'invoice', 'money back', 'overcharged']
    },
    'Login': {
        'title': 'Login & account access problems',
        'description': 'Inability to log in or access accounts, password reset issues, reset emails not received, unknown email linked to the subscription, and access inconsistencies across devices (TV, mobile, web).',
        'keywords': ['password', 'forgot password', 'reset password', 'cannot login', "can't log in", 'locked out', 'reset email', 'email not received', 'access']
    },
    'Technical': {
        'title': 'Technical / app issues',
        'description': 'App not loading, playback or streaming errors, buffering issues, content not starting, and general instability across devices.',
        'keywords': ['not working', 'app crash', 'buffering', 'streaming', 'playback', 'error code', 'video not load', 'frozen', 'black screen']
    },
    'Payment': {
        'title': 'Payment failures & payment method issues',
        'description': 'Card declined, payment rejected, difficulty updating payment details, retry payment requests, and subscriptions not activating due to payment errors.',
        'keywords': ['card declined', 'payment failed', 'payment rejected', 'update payment', 'card error', 'payment method', 'card expired']
    },
    'Partner': {
        'title': 'Partner subscription confusion (Amazon / Apple / Google / Sky)',
        'description': 'Uncertainty about where to manage or cancel subscriptions billed via partners and difficulty linking partner subscriptions to Paramount+ accounts.',
        'keywords': ['amazon', 'apple', 'google', 'sky', 'partner', 'roku', 'provider', 'bundle', 'third party']
    },
    'Content': {
        'title': 'Content availability & catalog issues',
        'description': 'Missing shows or episodes, content availability questions, search problems, catalog expectations not being met.',
        'keywords': ['ufc', 'yellowstone', 'content missing', 'show missing', 'episode', 'season', 'not available', 'where is', 'cannot find']
    },
    'Account': {
        'title': 'Account management issues',
        'description': 'Profile management problems, account settings, email changes, subscription status confusion, and unwanted account creation.',
        'keywords': ['account', 'profile', 'email change', 'update account', 'delete account', 'remove account', 'subscription status']
    }
}


def analyze_region_themes(df: pl.DataFrame, desc_col: str, total_cases: int) -> List[Dict]:
    """Analyze themes for a specific region's data."""
    if len(df) == 0:
        return []
    
    analyzer = TextAnalyzer()
    theme_counts = {theme: 0 for theme in THEME_NARRATIVES.keys()}
    theme_counts['Other'] = 0
    
    # Count themes based on keyword matching
    for row in df.iter_rows(named=True):
        text = str(row.get(desc_col, '') or '').lower()
        if not text:
            theme_counts['Other'] += 1
            continue
        
        matched = False
        for theme, info in THEME_NARRATIVES.items():
            for keyword in info['keywords']:
                if keyword in text:
                    theme_counts[theme] += 1
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            theme_counts['Other'] += 1
    
    # Calculate percentages and sort
    total = sum(theme_counts.values())
    if total == 0:
        return []
    
    results = []
    for theme, count in theme_counts.items():
        if count > 0 and theme != 'Other':
            pct = round(count / total * 100, 0)
            results.append({
                'theme': theme,
                'count': count,
                'percentage': pct,
                'title': THEME_NARRATIVES[theme]['title'],
                'description': THEME_NARRATIVES[theme]['description']
            })
    
    # Sort by percentage descending
    results.sort(key=lambda x: x['percentage'], reverse=True)
    return results


def get_subcategory_breakdown(df: pl.DataFrame, subcat_col: str, top_n: int = 7) -> pl.DataFrame:
    """Get sub-category breakdown with counts."""
    if subcat_col not in df.columns:
        return pl.DataFrame()
    
    return (
        df.filter(pl.col(subcat_col).is_not_null())
        .group_by(subcat_col)
        .agg(pl.count().alias('count'))
        .sort('count', descending=True)
        .head(top_n)
    )


def render_text_analytics(df: pl.DataFrame, config: Dict[str, Any]):
    """Render the Text Analytics module with rich regional insights."""
    
    st.header("Text Analytics")
    st.caption("Regional theme analysis from customer descriptions")
    
    processor = DataProcessor(df)
    total_cases = len(df)
    
    desc_col = processor.get_column('description')
    desc_trans_col = processor.get_column('description_translated')
    country_col = processor.get_column('country')
    subcat_col = processor.get_column('subcategory')
    cat_col = processor.get_column('category')
    issue_col = subcat_col if subcat_col else cat_col
    
    # Use best available description column
    analysis_col = desc_col if desc_col else desc_trans_col
    
    if not analysis_col:
        st.warning("No description column found in dataset.")
        st.info("Expected columns: Description (Column M) or Description Translation (Column V)")
        return
    
    if not country_col:
        st.warning("No country column found. Regional analysis requires a Country column.")
        return
    
    st.divider()
    
    # Get top regions
    top_regions = (
        df.filter(pl.col(country_col).is_not_null())
        .group_by(country_col)
        .agg(pl.count().alias('count'))
        .sort('count', descending=True)
        .head(10)
    )
    
    if len(top_regions) == 0:
        st.warning("No regional data available.")
        return
    
    # Region selector
    region_list = [str(r) for r in top_regions[country_col].to_list()]
    selected_region = st.selectbox("Select Region", region_list, key="text_region_select")
    
    # Filter to selected region
    region_df = df.filter(pl.col(country_col) == selected_region)
    region_volume = len(region_df)
    region_pct = round(region_volume / total_cases * 100, 1)
    
    st.divider()
    
    # Region header
    st.subheader(f"{selected_region}")
    st.caption(f"{region_volume:,} cases ({region_pct}% of total)")
    
    # Sub-category breakdown table
    if issue_col:
        st.markdown("**Sub-category Breakdown**")
        
        subcat_df = get_subcategory_breakdown(region_df, issue_col)
        
        if len(subcat_df) > 0:
            # Calculate percentage
            subcat_df = subcat_df.with_columns([
                (pl.col('count') / region_volume * 100).round(0).cast(pl.Int64).alias('pct')
            ])
            
            # Format for display
            display_df = subcat_df.to_pandas()
            display_df.columns = ['Sub-category', selected_region, '%']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Theme analysis
    st.markdown("**Trends by Region based on Description**")
    
    with st.spinner("Analyzing descriptions..."):
        themes = analyze_region_themes(region_df, analysis_col, region_volume)
    
    if not themes:
        st.info("Insufficient description data for theme analysis.")
        return
    
    # Display ranked themes with narratives
    for idx, theme in enumerate(themes, 1):
        if theme['percentage'] >= 2:  # Only show themes with 2%+ share
            st.markdown(f"""
**{idx}. {theme['title']} – {int(theme['percentage'])}%**

{theme['description']}
            """)
    
    st.divider()
    
    # Regional comparison (if more than one region)
    if len(region_list) > 1:
        st.subheader("Regional Comparison")
        st.caption("Theme distribution across top regions")
        
        # Analyze top 5 regions
        comparison_data = []
        
        for region in region_list[:5]:
            r_df = df.filter(pl.col(country_col) == region)
            r_themes = analyze_region_themes(r_df, analysis_col, len(r_df))
            
            row = {'Region': str(region), 'Volume': len(r_df)}
            for t in r_themes[:4]:  # Top 4 themes
                row[t['theme']] = f"{int(t['percentage'])}%"
            
            comparison_data.append(row)
        
        if comparison_data:
            comparison_df = pl.DataFrame(comparison_data)
            st.dataframe(comparison_df.to_pandas(), use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Key takeaways
    st.subheader("Key Takeaways")
    
    if themes:
        top_theme = themes[0]
        second_theme = themes[1] if len(themes) > 1 else None
        
        st.info(f"""
**Primary Driver: {top_theme['title']}**

At **{int(top_theme['percentage'])}%**, {top_theme['theme'].lower()}-related issues are the dominant theme in {selected_region}. 
{top_theme['description']}
        """)
        
        if second_theme and second_theme['percentage'] >= 15:
            st.info(f"""
**Secondary Driver: {second_theme['title']}**

At **{int(second_theme['percentage'])}%**, this is the second most common issue category requiring attention.
            """)
        
        # Calculate top 3 concentration
        top_3_pct = sum([t['percentage'] for t in themes[:3]])
        
        if top_3_pct >= 70:
            st.success(f"""
**High Concentration Opportunity**

The top 3 themes account for **{int(top_3_pct)}%** of issues in {selected_region}. 
Targeted fixes for these areas would address the majority of customer contacts.
            """)
        
        # Actionable recommendations
        st.subheader("Recommended Actions")
        
        for theme in themes[:3]:
            if theme['theme'] == 'Cancellation':
                st.markdown(f"- **{theme['theme']}**: Redesign cancellation UX with prominent 'Manage Subscription' button and pause options")
            elif theme['theme'] == 'Billing':
                st.markdown(f"- **{theme['theme']}**: Implement proactive billing notifications 48hrs before any charge")
            elif theme['theme'] == 'Login':
                st.markdown(f"- **{theme['theme']}**: Deploy SMS-based password reset with 24hr token validity")
            elif theme['theme'] == 'Technical':
                st.markdown(f"- **{theme['theme']}**: Prioritize app stability fixes and improve error messaging")
            elif theme['theme'] == 'Payment':
                st.markdown(f"- **{theme['theme']}**: Implement smart retry logic and clearer payment update flows")
            elif theme['theme'] == 'Partner':
                st.markdown(f"- **{theme['theme']}**: Escalate to Partner Engineering for API audit and integration fixes")
            elif theme['theme'] == 'Content':
                st.markdown(f"- **{theme['theme']}**: Improve search and implement content availability notifications")
            else:
                st.markdown(f"- **{theme['theme']}**: Expand self-service FAQ with localized content")
