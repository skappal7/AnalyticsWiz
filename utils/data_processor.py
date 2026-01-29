"""
Data Processing utilities using Polars and DuckDB
Optimized for 50K+ row datasets
"""

import io
from typing import Optional, Union, Dict, List, Any, Tuple
import polars as pl
import duckdb
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLUMN_MAPPING, DYNAMIC_COLUMNS


class DataProcessor:
    """
    High-performance data processor using Polars.
    Handles CSV, Excel, and Parquet files.
    """
    
    def __init__(self, df: pl.DataFrame):
        """
        Initialize processor with a Polars DataFrame.
        
        Args:
            df: Polars DataFrame to process
        """
        self.df = df
        self._column_cache = {}
        self._detect_columns()
    
    def _detect_columns(self):
        """Detect column names based on index and search patterns."""
        columns = self.df.columns
        
        # Map hardcoded positions
        for name, idx in COLUMN_MAPPING.items():
            if idx < len(columns):
                self._column_cache[name] = columns[idx]
        
        # Search for dynamic columns
        for name, patterns in DYNAMIC_COLUMNS.items():
            for col in columns:
                col_lower = col.lower()
                for pattern in patterns:
                    if pattern in col_lower:
                        self._column_cache[name] = col
                        break
                if name in self._column_cache:
                    break
    
    def get_column(self, name: str) -> Optional[str]:
        """
        Get the actual column name for a logical name.
        
        Args:
            name: Logical column name (e.g., 'country', 'category')
            
        Returns:
            Actual column name or None if not found
        """
        return self._column_cache.get(name)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset.
        
        Returns:
            Dictionary with total_rows, total_columns, memory_usage_mb
        """
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'memory_usage_mb': round(self.df.estimated_size() / (1024 * 1024), 2)
        }
    
    def get_top_n(self, column: str, n: int = 10) -> pl.DataFrame:
        """
        Get top N values by count for a column.
        
        Args:
            column: Column name to aggregate
            n: Number of top values to return
            
        Returns:
            DataFrame with value and count columns
        """
        if column not in self.df.columns:
            return pl.DataFrame()
        
        return (
            self.df
            .filter(pl.col(column).is_not_null())
            .group_by(column)
            .agg(pl.count().alias('count'))
            .sort('count', descending=True)
            .head(n)
        )
    
    def get_distribution(self, column: str) -> pl.DataFrame:
        """
        Get full distribution for a column with percentages.
        
        Args:
            column: Column name to analyze
            
        Returns:
            DataFrame with value, count, and percentage columns
        """
        if column not in self.df.columns:
            return pl.DataFrame()
        
        total = len(self.df)
        
        return (
            self.df
            .filter(pl.col(column).is_not_null())
            .group_by(column)
            .agg(pl.count().alias('count'))
            .with_columns([
                (pl.col('count') / total * 100).round(2).alias('percentage')
            ])
            .sort('count', descending=True)
        )
    
    def filter_sky_partners(self) -> pl.DataFrame:
        """
        Filter rows where partner contains 'sky' (case-insensitive).
        
        Returns:
            Filtered DataFrame with Sky partner rows only
        """
        partner_col = self.get_column('partner')
        if not partner_col or partner_col not in self.df.columns:
            return pl.DataFrame()
        
        return self.df.filter(
            pl.col(partner_col).is_not_null() & 
            pl.col(partner_col).str.to_lowercase().str.contains('sky')
        )
    
    def get_sky_partner_count(self) -> int:
        """Get count of Sky partner cases."""
        return len(self.filter_sky_partners())
    
    def get_sky_partner_percentage(self) -> float:
        """Get percentage of cases involving Sky partners."""
        total = len(self.df)
        if total == 0:
            return 0.0
        return round(self.get_sky_partner_count() / total * 100, 2)
    
    def get_weekly_aggregation(self) -> pl.DataFrame:
        """
        Aggregate data by week with volume and WoW changes.
        
        Returns:
            DataFrame with year, week, volume, wow_change, wow_pct columns
        """
        date_col = self.get_column('date')
        if not date_col or date_col not in self.df.columns:
            return pl.DataFrame()
        
        # Try to parse dates
        df = self._parse_dates(date_col)
        if df is None:
            return pl.DataFrame()
        
        # Filter out null dates
        df = df.filter(pl.col('_parsed_date').is_not_null())
        
        if len(df) == 0:
            return pl.DataFrame()
        
        # Aggregate by year-week
        weekly = (
            df
            .with_columns([
                # Truncate to Monday of the week
                pl.col('_parsed_date').dt.truncate("1w").alias('week_start')
            ])
            .group_by('week_start')
            .agg(pl.count().alias('volume'))
            .sort('week_start')
        )
        
        # Fill missing weeks (gap filling)
        if len(weekly) > 1:
            min_date = weekly['week_start'].min()
            max_date = weekly['week_start'].max()
            
            # Create full range
            full_range = pl.date_range(min_date, max_date, interval="1w", eager=True).alias("week_start")
            full_df = pl.DataFrame({"week_start": full_range})
            
            # Join and fill nulls with 0
            weekly = (
                full_df.join(weekly, on="week_start", how="left")
                .with_columns(pl.col("volume").fill_null(0))
            )

        # Create year/week columns for compatibility
        weekly = weekly.with_columns([
            pl.col('week_start').dt.year().alias('year'),
            pl.col('week_start').dt.week().alias('week'),
            (pl.col('week_start').dt.year() * 100 + pl.col('week_start').dt.week()).alias('week_idx')
        ]).sort('week_idx')
        
        # Calculate WoW changes
        weekly = weekly.with_columns([
            pl.col('volume').shift(1).alias('prev_volume')
        ])
        
        # Calculate WoW change (absolute and percentage)
        weekly = weekly.with_columns([
            (pl.col('volume').cast(pl.Int64) - pl.col('prev_volume').cast(pl.Int64)).alias('wow_change'),
            pl.when(pl.col('prev_volume').is_not_null() & (pl.col('prev_volume') > 0))
            .then(((pl.col('volume').cast(pl.Int64) - pl.col('prev_volume').cast(pl.Int64)) / pl.col('prev_volume') * 100).round(1))
            .otherwise(pl.lit(None))
            .alias('wow_pct')
        ])
        
        # Add trend classification
        weekly = weekly.with_columns([
            pl.when(pl.col('wow_pct').is_null()).then(pl.lit('N/A'))
            .when(pl.col('wow_pct') > 15).then(pl.lit('SPIKE'))
            .when(pl.col('wow_pct') > 5).then(pl.lit('UP'))
            .when(pl.col('wow_pct') < -10).then(pl.lit('DOWN'))
            .otherwise(pl.lit('FLAT'))
            .alias('trend')
        ])
        
        return weekly.select(['year', 'week', 'volume', 'wow_change', 'wow_pct', 'trend'])
    
    def _parse_dates(self, date_col: str) -> Optional[pl.DataFrame]:
        """
        Attempt to parse dates with multiple formats.
        
        Args:
            date_col: Date column name
            
        Returns:
            DataFrame with _parsed_date column or None if parsing fails
        """
        # First check if already datetime type
        if self.df[date_col].dtype in [pl.Date, pl.Datetime]:
            return self.df.with_columns([
                pl.col(date_col).cast(pl.Date).alias('_parsed_date')
            ])
        
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d/%m/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                df = self.df.with_columns([
                    pl.col(date_col).str.strptime(pl.Date, format=fmt, strict=False).alias('_parsed_date')
                ])
                # Check if any dates were parsed
                if df['_parsed_date'].null_count() < len(df):
                    return df
            except:
                continue
        
        # Try direct cast
        try:
            df = self.df.with_columns([
                pl.col(date_col).cast(pl.Date).alias('_parsed_date')
            ])
            return df
        except:
            pass
        
        # Try datetime then extract date
        try:
            df = self.df.with_columns([
                pl.col(date_col).cast(pl.Datetime).dt.date().alias('_parsed_date')
            ])
            return df
        except:
            pass
        
        return None
    
    def get_grouped_analysis(self, group_cols: List[str], 
                            filter_col: Optional[str] = None,
                            filter_pattern: Optional[str] = None) -> pl.DataFrame:
        """
        Get grouped analysis with volume and percentages.
        
        Args:
            group_cols: Columns to group by
            filter_col: Optional column to filter on
            filter_pattern: Optional pattern to match (case-insensitive)
            
        Returns:
            Grouped DataFrame with counts and percentages
        """
        df = self.df
        
        # Apply filter if specified
        if filter_col and filter_pattern and filter_col in df.columns:
            df = df.filter(
                pl.col(filter_col).is_not_null() &
                pl.col(filter_col).str.to_lowercase().str.contains(filter_pattern.lower())
            )
        
        # Validate columns exist
        valid_cols = [c for c in group_cols if c in df.columns]
        if not valid_cols:
            return pl.DataFrame()
        
        total = len(df)
        if total == 0:
            return pl.DataFrame()
        
        return (
            df
            .group_by(valid_cols)
            .agg(pl.count().alias('volume'))
            .with_columns([
                (pl.col('volume') / total * 100).round(2).alias('pct_of_total')
            ])
            .sort('volume', descending=True)
        )
    
    def execute_sql(self, query: str) -> pl.DataFrame:
        """
        Execute SQL query using DuckDB for complex operations.
        
        Args:
            query: SQL query (use 'df' as table name)
            
        Returns:
            Result as Polars DataFrame
        """
        conn = duckdb.connect(':memory:')
        conn.register('df', self.df.to_pandas())
        result = conn.execute(query).fetchdf()
        conn.close()
        return pl.from_pandas(result)


def load_data(file_source: Union[str, io.BytesIO], 
              filename: Optional[str] = None) -> pl.DataFrame:
    """
    Load data from various file formats.
    
    Args:
        file_source: File path or BytesIO object
        filename: Original filename (for BytesIO to detect format)
        
    Returns:
        Polars DataFrame
    """
    # Determine file type
    if isinstance(file_source, str):
        ext = file_source.lower().split('.')[-1]
    elif filename:
        ext = filename.lower().split('.')[-1]
    else:
        raise ValueError("Cannot determine file type without filename")
    
    # Load based on extension
    if ext == 'csv':
        return pl.read_csv(file_source, infer_schema_length=10000)
    elif ext in ['xlsx', 'xls']:
        return pl.read_excel(file_source)
    elif ext == 'parquet':
        return pl.read_parquet(file_source)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def get_unique_count(df: pl.DataFrame, column: str) -> int:
    """Get count of unique values in a column."""
    if column not in df.columns:
        return 0
    return df[column].n_unique()


def get_top_value(df: pl.DataFrame, column: str) -> Tuple[str, int]:
    """Get the most common value and its count."""
    if column not in df.columns:
        return ('N/A', 0)
    
    result = (
        df
        .filter(pl.col(column).is_not_null())
        .group_by(column)
        .agg(pl.count().alias('count'))
        .sort('count', descending=True)
        .head(1)
    )
    
    if len(result) == 0:
        return ('N/A', 0)
    
    return (str(result[column][0]), int(result['count'][0]))
