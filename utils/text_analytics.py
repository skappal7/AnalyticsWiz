"""
Text Analytics using keyword-based theme extraction
No ML dependencies - pure keyword matching with weighted scoring
"""

import re
from typing import Dict, Tuple, List, Optional
import polars as pl
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KEYWORDS


class TextAnalyzer:
    """Keyword-based text analyzer for theme extraction."""
    
    CLEANUP_PATTERNS = [
        re.compile(r'<external\s*email>', re.IGNORECASE),
        re.compile(r'sent from my (iphone|ipad|android)', re.IGNORECASE),
    ]
    
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    )
    
    def __init__(self, keywords: Optional[Dict] = None):
        self.keywords = keywords or KEYWORDS
    
    def clean_text(self, text: Optional[str]) -> str:
        if text is None or not isinstance(text, str):
            return ''
        result = text.lower()
        result = self.EMAIL_PATTERN.sub(' ', result)
        for pattern in self.CLEANUP_PATTERNS:
            result = pattern.sub(' ', result)
        return ' '.join(result.split())
    
    def categorize_text(self, text: Optional[str]) -> Tuple[str, int]:
        cleaned = self.clean_text(text)
        if not cleaned:
            return ('Unknown', 0)
        
        scores = {theme: 0 for theme in self.keywords.keys()}
        for theme, keyword_dict in self.keywords.items():
            for keyword, weight in keyword_dict.items():
                if keyword in cleaned:
                    scores[theme] += weight
        
        max_score = max(scores.values())
        if max_score == 0:
            return ('Unknown', 0)
        
        dominant_theme = max(scores.items(), key=lambda x: x[1])
        return dominant_theme
    
    def analyze_dataframe(self, df: pl.DataFrame, text_col: str,
                          fallback_col: Optional[str] = None) -> pl.DataFrame:
        if fallback_col and fallback_col in df.columns:
            df = df.with_columns([
                pl.when(pl.col(text_col).is_not_null() & (pl.col(text_col) != ''))
                .then(pl.col(text_col))
                .otherwise(pl.col(fallback_col))
                .alias('_combined_text')
            ])
            analysis_col = '_combined_text'
        else:
            analysis_col = text_col
        
        def categorize_row(text):
            return self.categorize_text(text)[0]
        
        def score_row(text):
            return self.categorize_text(text)[1]
        
        df = df.with_columns([
            pl.col(analysis_col).map_elements(categorize_row, return_dtype=pl.Utf8).alias('theme'),
            pl.col(analysis_col).map_elements(score_row, return_dtype=pl.Int64).alias('theme_score')
        ])
        
        if '_combined_text' in df.columns:
            df = df.drop('_combined_text')
        return df
    
    def get_theme_distribution(self, df: pl.DataFrame) -> pl.DataFrame:
        if 'theme' not in df.columns:
            return pl.DataFrame()
        total = len(df)
        return (
            df.group_by('theme')
            .agg(pl.count().alias('count'))
            .with_columns([(pl.col('count') / total * 100).round(2).alias('percentage')])
            .sort('count', descending=True)
        )
    
    def get_regional_themes(self, df: pl.DataFrame, country_col: str,
                           top_n: int = 5) -> Dict[str, pl.DataFrame]:
        if 'theme' not in df.columns or country_col not in df.columns:
            return {}
        
        # Filter out null countries first
        df_valid = df.filter(pl.col(country_col).is_not_null())
        
        top_countries = (
            df_valid.group_by(country_col).agg(pl.count().alias('count'))
            .sort('count', descending=True).head(top_n)
        )[country_col].to_list()
        
        result = {}
        for country in top_countries:
            if country is None:
                continue
            country_df = df_valid.filter(pl.col(country_col) == country)
            country_total = len(country_df)
            if country_total == 0:
                continue
            theme_dist = (
                country_df.group_by('theme').agg(pl.count().alias('count'))
                .with_columns([
                    (pl.col('count') / country_total * 100).round(2).alias('percentage'),
                    pl.when(pl.col('count') / country_total > 0.30).then(pl.lit('DOMINANT'))
                    .when(pl.col('count') / country_total > 0.20).then(pl.lit('HIGH'))
                    .when(pl.col('count') / country_total > 0.10).then(pl.lit('MODERATE'))
                    .otherwise(pl.lit('LOW')).alias('strength')
                ])
                .sort('count', descending=True)
            )
            result[str(country)] = theme_dist
        return result

    
    def get_insights(self, df: pl.DataFrame) -> Dict[str, str]:
        insights = {}
        if 'theme' not in df.columns:
            return {'error': 'No theme data available'}
        
        dist = self.get_theme_distribution(df)
        if len(dist) == 0:
            return {'error': 'Empty theme distribution'}
        
        top_theme = dist.row(0)
        insights['dominant_pattern'] = (
            f"{top_theme[0]} is the primary theme at {top_theme[2]:.1f}% "
            f"({top_theme[1]:,} mentions)."
        )
        
        top_3_pct = sum([row[2] for row in dist.head(3).iter_rows()])
        concentration = 'HIGH' if top_3_pct > 70 else ('MODERATE' if top_3_pct > 50 else 'DISTRIBUTED')
        insights['concentration'] = f"{concentration} concentration ({top_3_pct:.1f}% in top 3 themes)."
        
        recs = {
            'Cancellation': 'Redesign cancellation UX with retention offers',
            'Billing': 'Implement proactive billing notifications',
            'Login': 'Deploy SMS-based password reset',
            'Technical': 'Prioritize app stability fixes',
            'Payment': 'Add payment retry logic',
            'Partner': 'Escalate partner API issues',
            'Content': 'Address content availability gaps'
        }
        insights['recommendation'] = recs.get(top_theme[0], 'Expand self-service FAQ')
        return insights


def analyze_themes(df: pl.DataFrame, text_col: str,
                   fallback_col: Optional[str] = None) -> pl.DataFrame:
    analyzer = TextAnalyzer()
    return analyzer.analyze_dataframe(df, text_col, fallback_col)
