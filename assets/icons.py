"""
Lucide-style SVG Icons and UI Components
Proper HTML components that render correctly in Streamlit
"""

# Base64 embedded icons as data URIs for reliable rendering
# These are inline SVG strings that work with st.markdown(unsafe_allow_html=True)

ICONS = {
    'dashboard': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    'trending': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    'globe': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    'partner': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'search': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    'target': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    'text': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 6.1H3"/><path d="M21 12.1H3"/><path d="M15.1 18H3"/></svg>',
    'upload': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
    'shield': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    'chart': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
    'users': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'alert': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    'check': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    'arrow_up': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>',
    'arrow_down': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="m19 12-7 7-7-7"/></svg>',
    'clock': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    'zap': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>',
    'layers': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    'bar_chart': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    'pie_chart': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    'file_text': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    'sparkles': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/></svg>',
    'map': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/></svg>',
    'settings': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
}


def get_icon(name: str, size: int = 20, color: str = 'currentColor') -> str:
    """Get SVG icon by name."""
    svg = ICONS.get(name, ICONS.get('chart', ''))
    if size != 20:
        svg = svg.replace('width="20"', f'width="{size}"')
        svg = svg.replace('height="20"', f'height="{size}"')
    if color != 'currentColor':
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return svg


def icon_text(name: str, text: str, size: int = 18, color: str = '#64748b') -> str:
    """
    Create icon + text combination that renders properly in Streamlit.
    Returns HTML that works with st.markdown(unsafe_allow_html=True)
    """
    svg = get_icon(name, size, color)
    return f'''<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem">
<span style="display:flex;align-items:center">{svg}</span>
<span style="font-weight:600;color:#1e293b">{text}</span>
</div>'''


def section_header(title: str, icon_name: str, subtitle: str = '') -> str:
    """Generate a section header with icon - full HTML block."""
    icon = get_icon(icon_name, 24, '#2563eb')
    subtitle_html = f'<p style="color:#64748b;font-size:0.875rem;margin:0">{subtitle}</p>' if subtitle else ''
    return f'''
<div style="display:flex;align-items:center;gap:12px;margin-bottom:1.25rem;padding-bottom:0.75rem;border-bottom:1px solid #e2e8f0">
<div style="display:flex;align-items:center;justify-content:center;width:44px;height:44px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-radius:10px">
{icon}
</div>
<div>
<h2 style="margin:0;font-size:1.375rem;font-weight:700;color:#1e293b">{title}</h2>
{subtitle_html}
</div>
</div>
'''


def metric_card(value: str, label: str, icon_name: str, trend: str = None, trend_up: bool = True) -> str:
    """Generate a styled metric card with icon - complete HTML component."""
    icon = get_icon(icon_name, 24, '#2563eb')
    
    trend_html = ''
    if trend:
        trend_color = '#059669' if trend_up else '#dc2626'
        trend_arrow = get_icon('arrow_up' if trend_up else 'arrow_down', 14, trend_color)
        trend_html = f'<span style="display:inline-flex;align-items:center;gap:2px;color:{trend_color};font-size:0.75rem;font-weight:500">{trend_arrow}{trend}</span>'
    
    return f'''
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem">
<div style="display:flex;align-items:flex-start;justify-content:space-between">
<div>
<p style="color:#64748b;font-size:0.75rem;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 6px 0">{label}</p>
<div style="display:flex;align-items:baseline;gap:8px">
<span style="font-size:1.75rem;font-weight:700;color:#1e293b">{value}</span>
{trend_html}
</div>
</div>
<div style="display:flex;align-items:center;justify-content:center;width:44px;height:44px;background:#eff6ff;border-radius:10px">{icon}</div>
</div>
</div>
'''


def info_card(title: str, content: str, icon_name: str = 'info', color: str = 'blue') -> str:
    """
    Generate a styled info card - REPLACES st.info() for proper icon rendering.
    Use with st.markdown(card, unsafe_allow_html=True)
    """
    colors = {
        'blue': ('#2563eb', '#eff6ff', '#dbeafe'),
        'green': ('#059669', '#ecfdf5', '#d1fae5'),
        'yellow': ('#d97706', '#fffbeb', '#fef3c7'),
        'red': ('#dc2626', '#fef2f2', '#fee2e2'),
    }
    
    fg, bg, border = colors.get(color, colors['blue'])
    icon = get_icon(icon_name, 20, fg)
    
    return f'''
<div style="background:{bg};border-left:4px solid {fg};border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:0.5rem 0">
<div style="display:flex;align-items:flex-start;gap:12px">
<div style="flex-shrink:0;margin-top:2px">{icon}</div>
<div>
<p style="font-weight:600;color:{fg};margin:0 0 4px 0;font-size:0.9rem">{title}</p>
<p style="color:#475569;margin:0;font-size:0.875rem;line-height:1.5">{content}</p>
</div>
</div>
</div>
'''


def success_card(title: str, content: str) -> str:
    """Generate a success card - REPLACES st.success() for proper icon rendering."""
    return info_card(title, content, 'check', 'green')


def warning_card(title: str, content: str) -> str:
    """Generate a warning card - REPLACES st.warning() for proper icon rendering."""
    return info_card(title, content, 'alert', 'yellow')


def error_card(title: str, content: str) -> str:
    """Generate an error card - REPLACES st.error() for proper icon rendering."""
    return info_card(title, content, 'alert', 'red')


def priority_badge(priority: str) -> str:
    """Generate priority badge HTML."""
    colors = {
        'P0': ('#dc2626', '#fef2f2'),
        'P1': ('#ea580c', '#fff7ed'),
        'P2': ('#2563eb', '#eff6ff'),
        'CRITICAL': ('#dc2626', '#fef2f2'),
        'HIGH': ('#ea580c', '#fff7ed'),
        'MEDIUM': ('#d97706', '#fffbeb'),
        'LOW': ('#059669', '#ecfdf5')
    }
    
    fg, bg = colors.get(priority.upper(), ('#64748b', '#f1f5f9'))
    
    return f'<span style="background:{bg};color:{fg};padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;letter-spacing:0.025em">{priority}</span>'


# DEPRECATED - use icon_text instead
def icon_html(name: str, size: int = 20, color: str = '#64748b') -> str:
    """Legacy function - use icon_text() for better rendering."""
    svg = get_icon(name, size, color)
    return f'<span style="display:inline-flex;align-items:center;vertical-align:middle;margin-right:6px">{svg}</span>'
