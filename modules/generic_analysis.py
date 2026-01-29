"""
Module: Generic Analysis
Flexible analysis for any dataset with user-selected variables
"""

import streamlit as st
import polars as pl
import plotly.express as px
from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assets.icons import section_header, metric_card, info_card, success_card, warning_card, priority_badge, error_card
from utils.visualizations import ChartBuilder


def render_overview(df: pl.DataFrame, categorical_cols: List[str], numerical_cols: List[str]):
    """Render high-level overview of selected variables."""
    st.markdown(section_header("Analysis Overview", "dashboard", "Summary statistics for selected variables"), unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(metric_card(f"{len(df):,}", "Total Rows", "users"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(str(len(df.columns)), "Total Columns", "layers"), unsafe_allow_html=True)
    with col3:
        memory_mb = df.estimated_size() / (1024 * 1024)
        st.markdown(metric_card(f"{memory_mb:.1f} MB", "Memory Usage", "zap"), unsafe_allow_html=True)

    st.divider()
    
    # Categorical summary
    if categorical_cols:
        st.subheader("Categorical Variables")
        cols = st.columns(min(len(categorical_cols), 4))
        for idx, col in enumerate(categorical_cols[:4]):
            unique_count = df[col].n_unique()
            mode_result = df[col].mode()
            top_val = mode_result.item(0) if len(mode_result) > 0 else "N/A"
            with cols[idx]:
                st.metric(f"{col}", f"{unique_count} unique", f"Top: {top_val}")

    # Numerical summary
    if numerical_cols:
        st.subheader("Numerical Variables")
        st.dataframe(df.select(numerical_cols).describe(), use_container_width=True)

    # Narrative
    st.subheader("Automated Insights")
    
    if categorical_cols:
        col = categorical_cols[0]
        mode_res = df[col].mode()
        if len(mode_res) > 0:
            top_cat = mode_res.item(0)
            
            # Concentration Risk
            top_3_pct = 0
            count_df = df.group_by(col).agg(pl.count().alias('count')).sort('count', descending=True).head(3)
            if len(count_df) > 0:
                top_3_pct = round(count_df['count'].sum() / len(df) * 100, 1)
                
            count = len(df.filter(pl.col(col) == top_cat))
            pct = round(count / len(df) * 100, 1)
            
            if top_3_pct > 80:
                st.markdown(warning_card(
                    f"Action Required: High Concentration in {col}",
                    f"The top 3 categories account for **{top_3_pct}%** of all data. Dependency on **{top_cat}** ({pct}%) is critical. "
                    "**Recommendation:** Diversify or implement redundancy plans for these key segments."
                ), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    f"Dominant Segment: {col}",
                    f"**{top_cat}** is the leading category with **{pct}%** share. "
                    f"The distribution is relatively balanced, with the top 3 accounting for **{top_3_pct}%** of total volume.",
                    "pie_chart", "blue"
                ), unsafe_allow_html=True)
            
    if numerical_cols:
        col = numerical_cols[0]
        avg = df[col].mean()
        median = df[col].median()
        if avg and median:
            diff_pct = abs(avg - median) / median * 100 if median != 0 else 0
            
            if diff_pct > 20:
                st.markdown(info_card(
                    f"Metric Volatility: {col}",
                    f"The average (**{avg:,.2f}**) deviates from the median (**{median:,.2f}**) by **{diff_pct:.1f}%**, indicating significant usage of outliers or skewed data. "
                    "**Action:** Investigate extreme values that are pulling the average.",
                    "alert", "yellow"
                ), unsafe_allow_html=True)
            else:
                st.markdown(success_card(
                    f"Stable Metric: {col}",
                    f"The mean (**{avg:,.2f}**) and median (**{median:,.2f}**) are close, suggesting a normal, predictable distribution."
                ), unsafe_allow_html=True)
            
    if not categorical_cols and not numerical_cols:
        st.write("Select variables to generate insights.")

def render_distribution_analysis(df: pl.DataFrame, categorical_cols: List[str], numerical_cols: List[str]):
    """Render distribution analysis tab."""
    st.subheader("Distribution Analysis")
    
    col_type = st.radio("Select Variable Type", ["Categorical", "Numerical"], horizontal=True)
    
    if col_type == "Categorical" and categorical_cols:
        selected_col = st.selectbox("Select Variable", categorical_cols)
        
        # Calculate distribution
        dist = (
            df.group_by(selected_col)
            .agg(pl.count().alias('count'))
            .sort('count', descending=True)
            .head(20)
        )
        
        fig = px.bar(
            dist.to_pandas(), 
            x=selected_col, 
            y='count',
            title=f"Top 20 {selected_col} Distribution",
            color='count'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Narrative
        if len(dist) > 0:
            top_item = dist[selected_col][0]
            top_count = dist['count'][0]
            total = len(df)
            share = round(top_count / total * 100, 1)
            
            # Pareto Analysis
            cum_share = dist['count'].cumsum()
            pareto_idx = len(cum_share.filter(cum_share <= total * 0.8))
            pareto_pct = round(pareto_idx / dist[selected_col].n_unique() * 100, 1) if dist[selected_col].n_unique() > 0 else 0
            
            if share > 50:
                st.markdown(warning_card(
                    "Single Source Dependency",
                    f"**{top_item}** alone drives **{share}%** of all activity. Any issues affecting this category will have a systemic impact."
                ), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    f"The 'Vital Few' Insight",
                    f"**{top_item}** is the leader (**{share}%**). "
                    f"The top {len(dist)} categories capture **{round(dist['count'].sum() / total * 100, 1)}%** of the volume. "
                    "**Strategy:** Optimization efforts focused on these top categories will yield the highest ROI.",
                    "bar_chart", "blue"
                ), unsafe_allow_html=True)
        
    elif col_type == "Numerical" and numerical_cols:
        selected_col = st.selectbox("Select Variable", numerical_cols)
        
        fig = px.histogram(
            df.to_pandas(), 
            x=selected_col, 
            title=f"Distribution of {selected_col}",
            marginal="box"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Narrative
        stats = df[selected_col].describe()
        mean_val = df[selected_col].mean()
        median_val = df[selected_col].median()
        
        layout = "symmetric"
        if mean_val > median_val * 1.1:
            layout = "right-skewed (high outliers)"
        elif mean_val < median_val * 0.9:
            layout = "left-skewed (low outliers)"
            
        if layout.startswith("right") or layout.startswith("left"):
             st.markdown(warning_card(
                f"Skewed Distribution Detected - {layout}",
                f"The distribution is not symmetrical. 50% of values fall between **{df[selected_col].quantile(0.25):,.2f}** and **{df[selected_col].quantile(0.75):,.2f}**. "
                "**Action:** Use median instead of mean for forecasting to avoid outlier bias."
            ), unsafe_allow_html=True)
        else:
             st.markdown(success_card(
                "Normal Distribution",
                f"Data follows a standard bell curve pattern. Standard statistical models will be effective here."
            ), unsafe_allow_html=True)
        
    else:
        st.info(f"No {col_type.lower()} variables selected.")

def render_crosstab_analysis(df: pl.DataFrame, categorical_cols: List[str]):
    """Render cross-tabulation analysis."""
    st.subheader("Cross-Tabulation")
    
    if len(categorical_cols) < 2:
        st.warning("Select at least 2 categorical variables for cross-tabulation.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        row_var = st.selectbox("Row Variable", categorical_cols, index=0)
    with col2:
        col_var = st.selectbox("Column Variable", [c for c in categorical_cols if c != row_var], index=0)
        
    # Matrix chart
    crosstab = (
        df.group_by([row_var, col_var])
        .agg(pl.count().alias('count'))
        .sort('count', descending=True)
        .head(50)  # Limit for performance
    )
    
    fig = px.density_heatmap(
        crosstab.to_pandas(),
        x=col_var,
        y=row_var,
        z='count',
        title=f"Heatmap: {row_var} vs {col_var}",
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Narrative
    if len(crosstab) > 0:
        top_interaction = crosstab.row(0)
        r_val = top_interaction[0]
        c_val = top_interaction[1]
        cnt = top_interaction[2]
        pct = round(cnt / len(df) * 100, 1)
        
        msg = f"**{cnt:,}** cases found where **{row_var} = {r_val}** and **{col_var} = {c_val}**."
        
        if pct > 20:
            st.markdown(warning_card(
                "High-Volume Cluster Identified",
                f"{msg} This single combination accounts for **{pct}%** of the entire dataset. "
                "**Action:** Prioritize this specific segment for immediate impact."
            ), unsafe_allow_html=True)
        else:
            st.markdown(info_card(
                "Correlation Insight",
                f"{msg} This represents the strongest interaction in the dataset (**{pct}%** share).",
                "layers", "blue"
            ), unsafe_allow_html=True)

def render_time_analysis(df: pl.DataFrame, date_col: str, categorical_cols: List[str]):
    """Render user-defined time series analysis."""
    st.subheader("Time Series Analysis")
    
    if not date_col:
        st.warning("Please select a date column for time analysis.")
        return
        
    # Attempt to parse date if string
    try:
        if df[date_col].dtype == pl.Utf8:
            # Simple optimistic parsing
            temp_df = df.with_columns(pl.col(date_col).str.to_date(strict=False).alias('_parsed_date'))
        else:
            temp_df = df.with_columns(pl.col(date_col).alias('_parsed_date'))
            
        temp_df = temp_df.filter(pl.col('_parsed_date').is_not_null())
    except Exception as e:
        st.error(f"Could not parse date column: {e}")
        return

    # Aggregation selection
    interval = st.select_slider("Aggregation Interval", options=["Day", "Week", "Month"], value="Week")
    
    group_col = st.selectbox("Group By (Optional)", ["None"] + categorical_cols)
    
    if interval == "Day":
        trunc_str = "1d"
    elif interval == "Week":
        trunc_str = "1w"
    else:
        trunc_str = "1mo"
        
    # Build query
    if group_col != "None":
        time_data = (
            temp_df.sort('_parsed_date')
            .group_by_dynamic('_parsed_date', every=trunc_str, by=[group_col])
            .agg(pl.count().alias('count'))
        )
        fig = px.line(time_data.to_pandas(), x='_parsed_date', y='count', color=group_col, title="Volume Over Time")
    else:
        time_data = (
            temp_df.sort('_parsed_date')
            .group_by_dynamic('_parsed_date', every=trunc_str)
            .agg(pl.count().alias('count'))
        )
        fig = px.line(time_data.to_pandas(), x='_parsed_date', y='count', title="Volume Over Time")
        
    st.plotly_chart(fig, use_container_width=True)
    
    # Narrative
    if group_col == "None":
        total_intervals = len(time_data)
        if total_intervals > 1:
            start_vol = time_data['count'][0]
            end_vol = time_data['count'][-1]
            change = end_vol - start_vol
            pct_change = (change / start_vol * 100) if start_vol > 0 else 0
            
            trend = "Increasing" if change > 0 else "Decreasing"
            icon = "trending_up" if change > 0 else "trending_down"
            
            # Volatility check
            counts = time_data['count']
            std_dev = counts.std()
            mean_vol = counts.mean()
            cv = std_dev / mean_vol if mean_vol else 0
            
            volatility = "Stable"
            if cv > 0.5: volatility = "Highly Volatile"
            elif cv > 0.2: volatility = "Variable"
            
            trend_desc = "upward" if change > 0 else "downward"
            
            if volatility == "Highly Volatile":
                 st.markdown(warning_card(
                    f"Warning: highly Volatile Patterns",
                    f"Volume is changing drastically (CV: {cv:.2f}). "
                    f"While the overall trend is {trend_desc} (**{pct_change:+.1f}%**), predicting future volume will be difficult due to instability. "
                    "**Action:** Look for external drivers (campaigns, outages) causing these spikes."
                ), unsafe_allow_html=True)
            elif change > 10:
                st.markdown(success_card(
                    "Strong Growth Trajectory",
                    f"Volume has grown by **{pct_change:+.1f}%** over the period. "
                    f"Pattern is relatively stable. **Projection:** If this 30-day trend continues, expect volume to reach ~{int(end_vol * (1 + pct_change/100)):,} next period."
                ), unsafe_allow_html=True)
            elif change < -10:
                st.markdown(warning_card(
                    "Declining Volume Alert",
                    f"Volume has dropped by **{pct_change:.1f}%**. "
                    "**Action:** If this is a KPI, immediate intervention is needed to reverse the trend."
                ), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    "Stable Trend",
                    f"Volume is holding steady with minor fluctuations (**{pct_change:+.1f}%** change). "
                    "Operations can continue with current capacity planning.",
                    "activity", "blue"
                ), unsafe_allow_html=True)

def render_summary_infographic(df: pl.DataFrame, categorical_cols: List[str], numerical_cols: List[str], date_col: str):
    """Render a rich, non-redundant executive summary."""
    st.markdown(section_header("Executive Summary", "sparkles", "Automated Intelligence & Impact Analysis"), unsafe_allow_html=True)
    
    # 1. Data Health DNA (Non-redundant)
    # Focus on quality metrics not shown in the header
    row_count = len(df)
    completeness = 100 - (df.null_count().sum(axis=1).sum() / (row_count * len(df.columns)) * 100)
    duplicates = df.is_duplicated().sum()
    dup_pct = (duplicates / row_count) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(info_card("Data Health Score", f"**{completeness:.1f}%** Completeness", "shield", "blue"), unsafe_allow_html=True)
    with col2:
        if duplicates > 0:
            st.markdown(warning_card("Duplicate Check", f"**{duplicates:,}** duplicates found ({dup_pct:.1f}%)."), unsafe_allow_html=True)
        else:
            st.markdown(success_card("Clean Data", "No duplicates detected (100% unique records)."), unsafe_allow_html=True)
    with col3:
        # Sparsity check
        sparse_cols = [c for c in df.columns if df[c].null_count() > row_count * 0.5]
        if sparse_cols:
             st.markdown(warning_card("Sparsity Alert", f"**{len(sparse_cols)}** columns are >50% empty."), unsafe_allow_html=True)
        else:
             st.markdown(success_card("High Density", "All columns have good data coverage."), unsafe_allow_html=True)

    st.divider()

    # 2. Hero Insights: The "Golden Segments"
    # Identify what drives the numbers
    if numerical_cols and categorical_cols:
        target_num = numerical_cols[0]
        st.subheader(f"🏆 Key Drivers for {target_num}")
        
        # Analyze top 2 categorical columns for impact
        cols = st.columns(len(categorical_cols[:2]))
        
        for i, cat in enumerate(categorical_cols[:2]):
            with cols[i]:
                # Total Impact (Sum)
                agg_df = df.group_by(cat).agg([
                    pl.sum(target_num).alias('total'),
                    pl.mean(target_num).alias('avg')
                ]).sort('total', descending=True)
                
                top_segment = agg_df.row(0)
                seg_name = top_segment[0]
                seg_val = top_segment[1]
                seg_share = (seg_val / df[target_num].sum()) * 100
                
                st.markdown(f"**Top {cat} by Volume**")
                st.markdown(f"<h3 style='color:#2563eb;margin:0'>{seg_name}</h3>", unsafe_allow_html=True)
                st.markdown(f"Contributes **{seg_share:.1f}%** of total {target_num}.", unsafe_allow_html=True)
                
                # Mini bar chart for top 5
                top_5 = agg_df.head(5).to_pandas().set_index(cat)
                st.bar_chart(top_5['total'], color="#2563eb", height=150)

    elif numerical_cols:
         st.subheader(f"📊 {numerical_cols[0]} Distribution Pulse")
         st.bar_chart(df[numerical_cols[0]].to_pandas(), color="#2563eb", height=200)

    st.divider()

    # 3. Time Intelligence (Sparklines & Peaks)
    if date_col and date_col != "None":
        st.subheader("📈 Temporal Pulse")
        try:
            # Parse date
            if df[date_col].dtype == pl.Utf8:
                date_df = df.with_columns(pl.col(date_col).str.to_date(strict=False).alias('_d')).drop_nulls('_d')
            else:
                date_df = df.with_columns(pl.col(date_col).alias('_d')).drop_nulls('_d')
            
            # Aggregate by month for trend
            trend = date_df.sort('_d').group_by_dynamic('_d', every='1mo').agg(
                pl.count().alias('records'),
                pl.sum(numerical_cols[0]).alias('value') if numerical_cols else pl.count().alias('value')
            )
            
            # Find Peak
            peak_row = trend.sort('value', descending=True).row(0)
            peak_date = peak_row[0].strftime('%B %Y')
            peak_val = peak_row[2]
            
            metric_label = numerical_cols[0] if numerical_cols else "Record Count"
            
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown(info_card(
                    "Peak Performance",
                    f"Highest {metric_label} observed in **{peak_date}** with **{peak_val:,.0f}**.",
                    "trending", "green"
                ), unsafe_allow_html=True)
            with c2:
                # Sparkline
                st.area_chart(trend.to_pandas().set_index('_d')['value'], color="#059669", height=150)
                
        except Exception as e:
            st.warning(f"Could not render timeline: {e}")
            
    # 4. Correlation Radar (Quick check)
    if len(numerical_cols) >= 2:
        st.divider()
        st.subheader("🔗 Correlation Radar")
        
        corr_val = df.select(pl.corr(numerical_cols[0], numerical_cols[1])).item(0, 0)
        strong = abs(corr_val) > 0.7
        relation = "Positive" if corr_val > 0 else "Negative"
        
        msg = f"**{numerical_cols[0]}** and **{numerical_cols[1]}** have a **{strong and 'Strong ' or 'Weak '}{relation}** correlation ({corr_val:.2f})."
        
        if strong:
            st.markdown(success_card("Key Relationship Found", msg), unsafe_allow_html=True)
        else:
            st.info(msg)


def render_generic_analysis(df: pl.DataFrame):
    """Main entry point for Generic Analysis."""
    
    # Variable selection in sidebar is handled in app.py, but we can also do it here if needed.
    # For now, let's assume we pass the configuration or let user select here.
    # To keep it "Analysis for All" style, let's put selectors at the top.
    
    with st.expander("Analysis Configuration", expanded=True):
        all_cols = df.columns
        
        # Guess types
        num_cols = [c for c in all_cols if df[c].dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]]
        cat_cols = [c for c in all_cols if c not in num_cols]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_cat = st.multiselect("Categorical Variables", cat_cols, default=cat_cols[:2] if len(cat_cols)>1 else cat_cols)
        with col2:
            selected_num = st.multiselect("Numerical Variables", num_cols, default=num_cols[:2] if len(num_cols)>1 else num_cols)
        with col3:
            # Date column guess
            date_candidates = [c for c in all_cols if "date" in c.lower() or "time" in c.lower()]
            selected_date = st.selectbox("Date Column (for Time Analysis)", ["None"] + all_cols, index=all_cols.index(date_candidates[0])+1 if date_candidates else 0)

    # Tabs
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Overview", "Trends", "Distribution", "Cross-Tab"])
    
    with tab0:
        render_summary_infographic(df, selected_cat, selected_num, selected_date)

    with tab1:
        render_overview(df, selected_cat, selected_num)
        
    with tab2:
        if selected_date != "None":
            render_time_analysis(df, selected_date, selected_cat)
        else:
            st.info("Select a Date Column to view time trends.")
            
    with tab3:
        render_distribution_analysis(df, selected_cat, selected_num)
        
    with tab4:
        render_crosstab_analysis(df, selected_cat)
