"""
Configuration settings for Data Storyteller Analytics App
"""

# Column mappings (0-based indexing for Polars)
COLUMN_MAPPING = {
    'queue': 0,                      # Column A (index 0)
    'date': 9,                       # Column J (index 9)
    'description': 12,               # Column M (index 12)
    'partner': 18,                   # Column S (index 18)
    'country': 20,                   # Column U (index 20)
    'description_translated': 21    # Column V (index 21)
}

# Dynamic column search patterns (case-insensitive)
DYNAMIC_COLUMNS = {
    'category': ['category', 'cat'],
    'subcategory': ['sub-category', 'subcategory', 'issue', 'reason']
}

# Color scheme - Professional muted palette
COLORS = {
    'primary': '#2563eb',
    'primary_dark': '#1d4ed8',
    'secondary': '#64748b',
    'danger': '#dc2626',
    'success': '#059669',
    'warning': '#d97706',
    'info': '#0284c7',
    'critical': '#dc2626',
    'high': '#ea580c',
    'medium': '#d97706',
    'low': '#059669',
    'text_primary': '#1e293b',
    'text_secondary': '#475569',
    'text_muted': '#64748b',
    'bg_secondary': '#f8fafc',
    'border': '#e2e8f0'
}

# Chart color palette - Professional muted
CHART_COLORS = [
    '#2563eb',  # Blue
    '#059669',  # Green
    '#d97706',  # Amber
    '#dc2626',  # Red
    '#7c3aed',  # Purple
    '#0284c7',  # Sky
    '#64748b',  # Slate
    '#ea580c',  # Orange
]


# Cost assumptions
COST_PER_CASE = 10  # USD
MONTHS_PER_YEAR = 12

# Keyword dictionary for text analytics
KEYWORDS = {
    'Cancellation': {
        'cancel': 1, 'unsubscribe': 1, 'terminate': 1,
        'how to cancel': 2, 'cannot cancel': 2, 'unable to cancel': 2,
        'stop subscription': 2, 'end subscription': 2, 'free trial': 1
    },
    'Billing': {
        'refund': 2, 'charged': 2, 'unexpected charge': 3,
        'double bill': 3, 'charge after cancel': 3, 'billing': 1,
        'invoice': 1, 'money back': 2
    },
    'Login': {
        'password': 2, 'forgot password': 3, 'reset password': 3,
        'cannot login': 3, "can't log in": 3, 'unable to login': 3,
        'locked out': 3, 'reset email': 2, 'email not received': 2
    },
    'Technical': {
        'not working': 2, 'app crash': 3, 'buffering': 2,
        'streaming': 1, 'playback': 2, 'error code': 2,
        'video not load': 2, 'app not load': 3, 'frozen': 2
    },
    'Payment': {
        'card declined': 3, 'payment failed': 3, 'payment rejected': 3,
        'update payment': 2, 'card error': 2, 'payment method': 2
    },
    'Partner': {
        'amazon': 1, 'apple': 1, 'google': 1, 'sky': 2, 'partner': 1
    },
    'Content': {
        'ufc': 3, 'yellowstone': 3, 'content missing': 2,
        'show missing': 2, 'episode': 1, 'season': 1
    }
}

# Severity thresholds (percentages)
SEVERITY_THRESHOLDS = {
    'critical': 15,
    'high': 8,
    'medium': 4
}

# Trend thresholds (percentages)
TREND_THRESHOLDS = {
    'spike': 15,
    'up': 5,
    'down': -10
}

# Recommendation templates
RECOMMENDATIONS = {
    'password': {
        'action': 'Deploy SMS-based password reset',
        'detail': 'Extend token validity to 24 hours',
        'effort': '2-3 weeks',
        'reduction': 0.70
    },
    'cancel': {
        'action': 'Redesign cancellation UX flow',
        'detail': "Add prominent 'Manage Subscription' button",
        'effort': '1-2 weeks',
        'reduction': 0.10
    },
    'bill': {
        'action': 'Proactive billing notifications',
        'detail': 'Send reminders 48hrs before charge',
        'effort': '1 week',
        'reduction': 0.05
    },
    'sky': {
        'action': 'Escalate Sky API integration fix',
        'detail': 'Rewrite Partner Engineering handshake',
        'effort': '3-4 weeks',
        'reduction': 0.80
    },
    'default': {
        'action': 'Expand self-service FAQ',
        'detail': 'Create localized content for top 3 issues',
        'effort': '2 weeks',
        'reduction': 0.08
    }
}
