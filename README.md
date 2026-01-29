# Paramount+ Customer Analytics

Production-ready Streamlit application for contact center analytics with GDPR-compliant PII redaction.

## Features

- **7 Analytics Modules**: Executive Dashboard, Time Intelligence, Sky Partner Analysis, Regional Deep Dive, Root Cause Analysis, Recommendations, Text Analytics
- **GDPR-Compliant PII Redaction**: Regex-based redaction of emails, phone numbers, credit cards, and names
- **High Performance**: Optimized for 50K+ rows using Polars and DuckDB
- **No Emojis**: All UI icons are pure SVG
- **Streamlit Cloud Compatible**: No ML dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Data Structure

**Expected Column Positions (0-indexed):**
- Column A (0): Queue Name
- Column J (9): Date/Time
- Column M (12): Description
- Column S (18): Partner
- Column U (20): Country
- Column V (21): Description Translation

**Dynamic Columns (auto-detected):**
- Category / Cat
- Sub-Category / Issue / Reason

## Supported File Formats

- CSV (.csv)
- Excel (.xlsx)
- Parquet (.parquet)

## Modules

1. **Executive Dashboard**: KPIs, charts, strategic insights
2. **Time Intelligence**: Weekly trends, WoW analysis
3. **Sky Partner Analysis**: Two-level partner deep dive
4. **Regional Deep Dive**: Market-by-market analysis
5. **Root Cause Analysis**: Issue severity classification
6. **Recommendations**: Prioritized action plan with ROI
7. **Text Analytics**: Keyword-based theme extraction

## License

Proprietary - Paramount+ Internal Use Only
