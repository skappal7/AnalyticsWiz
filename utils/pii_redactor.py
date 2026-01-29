"""
GDPR-Compliant PII Redactor
Uses regex patterns to redact personally identifiable information
"""

import re
from typing import Optional
import polars as pl


class PIIRedactor:
    """
    Regex-based PII redaction for GDPR/CCPA/DPA compliance.
    No ML dependencies - pure regex patterns.
    """
    
    # Compiled regex patterns for performance
    PATTERNS = {
        'EMAIL': re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        ),
        'PHONE': re.compile(
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ),
        'CREDIT_CARD': re.compile(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        ),
        'IP_ADDRESS': re.compile(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ),
        'URL': re.compile(
            r'https?://[^\s]+'
        ),
        'SSN': re.compile(
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        )
    }
    
    # Name patterns (titles + names)
    NAME_PATTERNS = [
        re.compile(r'\b(Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'),
        re.compile(r'\bDear\s+[A-Z][a-z]+\b', re.IGNORECASE),
        re.compile(r'\bHi\s+[A-Z][a-z]+\b', re.IGNORECASE),
        re.compile(r'\bHello\s+[A-Z][a-z]+\b', re.IGNORECASE),
    ]
    
    # Redaction placeholders
    PLACEHOLDERS = {
        'EMAIL': '[EMAIL_REDACTED]',
        'PHONE': '[PHONE_REDACTED]',
        'CREDIT_CARD': '[CREDIT_CARD_REDACTED]',
        'IP_ADDRESS': '[IP_REDACTED]',
        'URL': '[URL_REDACTED]',
        'SSN': '[SSN_REDACTED]',
        'NAME': '[NAME_REDACTED]'
    }
    
    def __init__(self, redact_emails: bool = True, redact_phones: bool = True,
                 redact_names: bool = True, redact_cards: bool = True,
                 redact_ips: bool = True, redact_urls: bool = False):
        """
        Initialize redactor with configurable options.
        
        Args:
            redact_emails: Redact email addresses
            redact_phones: Redact phone numbers
            redact_names: Redact detected names
            redact_cards: Redact credit card numbers
            redact_ips: Redact IP addresses
            redact_urls: Redact URLs (disabled by default)
        """
        self.redact_emails = redact_emails
        self.redact_phones = redact_phones
        self.redact_names = redact_names
        self.redact_cards = redact_cards
        self.redact_ips = redact_ips
        self.redact_urls = redact_urls
    
    def redact_text(self, text: Optional[str]) -> str:
        """
        Redact PII from a single text string.
        
        Args:
            text: Input text that may contain PII
            
        Returns:
            Text with PII replaced by placeholders
        """
        if text is None or not isinstance(text, str) or text.strip() == '':
            return text if text else ''
        
        result = text
        
        # Redact emails
        if self.redact_emails:
            result = self.PATTERNS['EMAIL'].sub(self.PLACEHOLDERS['EMAIL'], result)
        
        # Redact phone numbers
        if self.redact_phones:
            result = self.PATTERNS['PHONE'].sub(self.PLACEHOLDERS['PHONE'], result)
        
        # Redact credit cards
        if self.redact_cards:
            result = self.PATTERNS['CREDIT_CARD'].sub(self.PLACEHOLDERS['CREDIT_CARD'], result)
        
        # Redact IP addresses
        if self.redact_ips:
            result = self.PATTERNS['IP_ADDRESS'].sub(self.PLACEHOLDERS['IP_ADDRESS'], result)
        
        # Redact URLs
        if self.redact_urls:
            result = self.PATTERNS['URL'].sub(self.PLACEHOLDERS['URL'], result)
        
        # Redact names (using title patterns)
        if self.redact_names:
            for pattern in self.NAME_PATTERNS:
                result = pattern.sub(self.PLACEHOLDERS['NAME'], result)
        
        return result
    
    def redact_dataframe(self, df: pl.DataFrame, columns: list) -> pl.DataFrame:
        """
        Redact PII from specified columns in a Polars DataFrame.
        
        Args:
            df: Polars DataFrame
            columns: List of column names to redact
            
        Returns:
            DataFrame with PII redacted from specified columns
        """
        for col in columns:
            if col in df.columns:
                # Use map_elements for custom function application
                df = df.with_columns([
                    pl.col(col).map_elements(
                        self.redact_text,
                        return_dtype=pl.Utf8
                    ).alias(col)
                ])
        
        return df
    
    def get_stats(self, text: str) -> dict:
        """
        Get statistics about PII found in text (without redacting).
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with counts of each PII type found
        """
        if not text:
            return {key: 0 for key in self.PATTERNS.keys()}
        
        stats = {}
        for pii_type, pattern in self.PATTERNS.items():
            stats[pii_type] = len(pattern.findall(text))
        
        # Count names
        name_count = 0
        for pattern in self.NAME_PATTERNS:
            name_count += len(pattern.findall(text))
        stats['NAME'] = name_count
        
        return stats


def redact_pii(df: pl.DataFrame, columns: list, 
               redact_emails: bool = True, redact_phones: bool = True,
               redact_names: bool = True, redact_cards: bool = True) -> pl.DataFrame:
    """
    Convenience function to redact PII from a DataFrame.
    
    Args:
        df: Polars DataFrame
        columns: List of column names to redact
        redact_emails: Redact email addresses
        redact_phones: Redact phone numbers
        redact_names: Redact detected names
        redact_cards: Redact credit card numbers
        
    Returns:
        DataFrame with PII redacted
    """
    redactor = PIIRedactor(
        redact_emails=redact_emails,
        redact_phones=redact_phones,
        redact_names=redact_names,
        redact_cards=redact_cards
    )
    return redactor.redact_dataframe(df, columns)
