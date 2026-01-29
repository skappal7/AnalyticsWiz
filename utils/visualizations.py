"""
Plotly Visualization utilities
Professional muted styling for all charts
"""

from typing import Optional, List
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import COLORS, CHART_COLORS
except ImportError:
    COLORS = {'primary': '#2563eb', 'danger': '#dc2626', 'secondary': '#64748b'}
    CHART_COLORS = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0284c7']


class ChartBuilder:
    """Plotly chart builder with professional muted styling."""
    
    DEFAULT_TEMPLATE = 'plotly_white'
    
    # Professional muted palette
    COLOR_PALETTE = CHART_COLORS if 'CHART_COLORS' in dir() else [
        '#2563eb',  # Blue
        '#059669',  # Green  
        '#d97706',  # Amber
        '#dc2626',  # Red
        '#7c3aed',  # Purple
        '#0284c7',  # Sky
        '#64748b',  # Slate
        '#ea580c',  # Orange
    ]
    
    # Chart font settings
    FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    TITLE_SIZE = 14
    AXIS_LABEL_SIZE = 12
    TICK_SIZE = 11
    
    def __init__(self, height: int = 400):
        self.height = height
    
    def _apply_common_layout(self, fig: go.Figure, title: str = '') -> go.Figure:
        """Apply consistent styling to all charts."""
        fig.update_layout(
            template=self.DEFAULT_TEMPLATE,
            height=self.height,
            title={
                'text': title,
                'font': {'size': self.TITLE_SIZE, 'family': self.FONT_FAMILY, 'color': '#1e293b'},
                'x': 0,
                'xanchor': 'left'
            },
            font={'family': self.FONT_FAMILY, 'size': self.TICK_SIZE, 'color': '#475569'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 40, 'r': 20, 't': 40, 'b': 40},
            showlegend=False
        )
        
        # Grid styling
        fig.update_xaxes(
            gridcolor='#e2e8f0',
            linecolor='#e2e8f0',
            tickfont={'size': self.TICK_SIZE, 'color': '#64748b'}
        )
        fig.update_yaxes(
            gridcolor='#e2e8f0', 
            linecolor='#e2e8f0',
            tickfont={'size': self.TICK_SIZE, 'color': '#64748b'}
        )
        
        return fig
    
    def create_bar_chart(self, df: pl.DataFrame, x: str, y: str,
                         title: str = '', horizontal: bool = True,
                         color: str = None) -> go.Figure:
        """Create bar chart with optional horizontal orientation."""
        pdf = df.to_pandas()
        bar_color = color or self.COLOR_PALETTE[0]
        
        if horizontal:
            fig = go.Figure(go.Bar(
                x=pdf[y],
                y=pdf[x],
                orientation='h',
                marker_color=bar_color,
                marker_line_width=0
            ))
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        else:
            fig = go.Figure(go.Bar(
                x=pdf[x],
                y=pdf[y],
                marker_color=bar_color,
                marker_line_width=0
            ))
        
        return self._apply_common_layout(fig, title)
    
    def create_pie_chart(self, df: pl.DataFrame, names: str, values: str,
                         title: str = '', hole: float = 0.45) -> go.Figure:
        """Create donut chart with percentages."""
        pdf = df.to_pandas()
        
        fig = go.Figure(go.Pie(
            labels=pdf[names],
            values=pdf[values],
            hole=hole,
            marker_colors=self.COLOR_PALETTE[:len(pdf)],
            textposition='inside',
            textinfo='percent',
            textfont={'size': 12, 'color': 'white'},
            hovertemplate='%{label}: %{value:,}<br>%{percent}<extra></extra>'
        ))
        
        fig.update_layout(
            template=self.DEFAULT_TEMPLATE,
            height=self.height,
            title={
                'text': title,
                'font': {'size': self.TITLE_SIZE, 'family': self.FONT_FAMILY, 'color': '#1e293b'},
                'x': 0,
                'xanchor': 'left'
            },
            font={'family': self.FONT_FAMILY},
            paper_bgcolor='rgba(0,0,0,0)',
            margin={'l': 20, 'r': 20, 't': 40, 'b': 20},
            showlegend=True,
            legend={
                'orientation': 'v',
                'yanchor': 'middle',
                'y': 0.5,
                'xanchor': 'left',
                'x': 1.02,
                'font': {'size': 11, 'color': '#475569'}
            }
        )
        return fig
    
    def create_line_chart(self, df: pl.DataFrame, x: str, y: str,
                          title: str = '', show_average: bool = True,
                          markers: bool = True) -> go.Figure:
        """Create line chart with optional average line."""
        pdf = df.to_pandas()
        
        fig = go.Figure()
        
        # Main line
        fig.add_trace(go.Scatter(
            x=pdf[x],
            y=pdf[y],
            mode='lines+markers' if markers else 'lines',
            line={'color': self.COLOR_PALETTE[0], 'width': 2},
            marker={'size': 6, 'color': self.COLOR_PALETTE[0]},
            hovertemplate='%{x}<br>Volume: %{y:,}<extra></extra>'
        ))
        
        # Average line
        if show_average and y in pdf.columns:
            avg = pdf[y].mean()
            fig.add_hline(
                y=avg,
                line_dash="dash",
                line_color='#64748b',
                line_width=1,
                annotation_text=f"Avg: {avg:,.0f}",
                annotation_position="top right",
                annotation_font={'size': 11, 'color': '#64748b'}
            )
        
        return self._apply_common_layout(fig, title)
    
    def create_grouped_bar(self, df: pl.DataFrame, x: str, y: str,
                           color: str, title: str = '') -> go.Figure:
        """Create grouped bar chart."""
        pdf = df.to_pandas()
        
        fig = px.bar(pdf, x=x, y=y, color=color, title=title, barmode='group',
                     color_discrete_sequence=self.COLOR_PALETTE)
        
        return self._apply_common_layout(fig, title)
    
    def create_treemap(self, df: pl.DataFrame, path: List[str], values: str,
                       title: str = '') -> go.Figure:
        """Create treemap visualization."""
        pdf = df.to_pandas()
        
        fig = px.treemap(pdf, path=path, values=values, title=title,
                         color_discrete_sequence=self.COLOR_PALETTE)
        
        fig.update_layout(
            template=self.DEFAULT_TEMPLATE,
            height=self.height,
            font={'family': self.FONT_FAMILY}
        )
        return fig


def create_severity_badge(severity: str) -> str:
    """Generate HTML for severity badge."""
    colors = {
        'CRITICAL': ('#dc2626', '#FFFFFF'),
        'HIGH': ('#ea580c', '#FFFFFF'),
        'MEDIUM': ('#d97706', '#FFFFFF'),
        'LOW': ('#059669', '#FFFFFF'),
        'SPIKE': ('#dc2626', '#FFFFFF'),
        'UP': ('#059669', '#FFFFFF'),
        'DOWN': ('#dc2626', '#FFFFFF'),
        'FLAT': ('#64748b', '#FFFFFF'),
        'DOMINANT': ('#2563eb', '#FFFFFF'),
        'MODERATE': ('#d97706', '#FFFFFF')
    }
    
    bg, fg = colors.get(severity.upper(), ('#64748b', '#FFFFFF'))
    
    return f'''
    <span style="
        background-color: {bg};
        color: {fg};
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    ">{severity}</span>
    '''
