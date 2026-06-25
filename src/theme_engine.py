import streamlit as st

def get_theme_css(theme_name: str) -> str:
    themes = {
        "Midnight Pro (Dark)": {
            "--bg-primary": "#121212",
            "--bg-secondary": "#1E1E1E",
            "--bg-card": "#252525",
            "--text-primary": "#FFFFFF",
            "--text-secondary": "#AAAAAA",
            "--accent-color": "#4DA8DA",
            "--border-color": "#333333",
            "--shadow-color": "rgba(0, 0, 0, 0.5)",
            "--shadow-color-hover": "rgba(77, 168, 218, 0.4)"
        },
        "Cyberpunk (Dark)": {
            "--bg-primary": "#0D0E15",
            "--bg-secondary": "#13141F",
            "--bg-card": "#1A1A2E",
            "--text-primary": "#00FFFF",
            "--text-secondary": "#E94560",
            "--accent-color": "#FF2E93",
            "--border-color": "#FF2E93",
            "--shadow-color": "rgba(255, 46, 147, 0.2)",
            "--shadow-color-hover": "rgba(0, 255, 255, 0.5)"
        },
        "Deep Ocean (Dark)": {
            "--bg-primary": "#051923",
            "--bg-secondary": "#003554",
            "--bg-card": "#006494",
            "--text-primary": "#FFFFFF",
            "--text-secondary": "#EBF4FA",
            "--accent-color": "#00A6FB",
            "--border-color": "#0582CA",
            "--shadow-color": "rgba(0, 0, 0, 0.5)",
            "--shadow-color-hover": "rgba(0, 166, 251, 0.4)"
        },
        "Clean White (Light)": {
            "--bg-primary": "#F9FAFB",
            "--bg-secondary": "#F3F4F6",
            "--bg-card": "#FFFFFF",
            "--text-primary": "#111827",
            "--text-secondary": "#6B7280",
            "--accent-color": "#2563EB",
            "--border-color": "#E5E7EB",
            "--shadow-color": "rgba(0, 0, 0, 0.05)",
            "--shadow-color-hover": "rgba(37, 99, 235, 0.2)"
        },
        "Sunset Glow (Light)": {
            "--bg-primary": "#FFF9F5",
            "--bg-secondary": "#FFE8D6",
            "--bg-card": "#FFFFFF",
            "--text-primary": "#2D3142",
            "--text-secondary": "#4F5D75",
            "--accent-color": "#EF8354",
            "--border-color": "#FFC09F",
            "--shadow-color": "rgba(0, 0, 0, 0.05)",
            "--shadow-color-hover": "rgba(239, 131, 84, 0.3)"
        },
        "Mint Light (Light)": {
            "--bg-primary": "#F2FDF5",
            "--bg-secondary": "#E5F9E0",
            "--bg-card": "#FFFFFF",
            "--text-primary": "#143601",
            "--text-secondary": "#538D22",
            "--accent-color": "#248232",
            "--border-color": "#A3C9A8",
            "--shadow-color": "rgba(0, 0, 0, 0.05)",
            "--shadow-color-hover": "rgba(36, 130, 50, 0.3)"
        }
    }
    
    # Fallback to Midnight Pro if not found
    sel_theme = themes.get(theme_name, themes["Midnight Pro (Dark)"])
    
    css_vars = ""
    for k, v in sel_theme.items():
        css_vars += f"{k}: {v};\n"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    :root {{
        {css_vars}
    }}

    /* Global Font Override */
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif !important;
    }}

    /* App Background */
    [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-primary);
        color: var(--text-primary) !important;
    }}
    
    /* Header (top bar) */
    [data-testid="stHeader"] {{
        background-color: var(--bg-primary);
    }}

    /* Sidebar Background */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-secondary) !important;
    }}

    /* 3D Hover Cards for Metrics */
    [data-testid="stMetric"] {{
        background-color: var(--bg-card) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px var(--shadow-color) !important;
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border: 1px solid var(--border-color) !important;
    }}

    [data-testid="stMetric"]:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0 12px 20px var(--shadow-color-hover) !important;
    }}

    /* Custom Signal Card Styling (Matches Metric Cards) */
    .custom-signal-card {{
        background-color: var(--bg-card) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px var(--shadow-color) !important;
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border: 1px solid var(--border-color) !important;
        display: flex;
        flex-direction: column;
    }}
    .custom-signal-card:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0 12px 20px var(--shadow-color-hover) !important;
    }}
    .custom-signal-label {{
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.9rem;
        margin-bottom: 0px;
    }}
    .custom-signal-value {{
        font-size: 1.8rem;
        font-weight: 700 !important;
        line-height: 1.2;
    }}

    /* Metric Text Coloring */
    [data-testid="stMetricLabel"] {{
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--accent-color) !important;
        font-weight: 700 !important;
    }}

    /* General Typography Fixes to ensure readability across themes */
    p, h1, h2, h3, h4, h5, h6, label, li, 
    [data-testid="stMarkdownContainer"] p, 
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {{
        color: var(--text-primary) !important;
    }}
    
    /* Hide MS Edge Native Password Reveal Icon (prevents double eye icons) */
    input[type="password"]::-ms-reveal,
    input[type="password"]::-ms-clear {{
        display: none !important;
    }}

    /* Fix Dropdown Menu visibility in Dark Mode */
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {{
        background-color: var(--bg-card) !important;
    }}
    [data-baseweb="menu"] li {{
        color: var(--text-primary) !important;
    }}
    [data-baseweb="menu"] li:hover {{
        background-color: var(--bg-primary) !important;
    }}

    /* Style Tabs as Floating Cards */
    [data-testid="stTabs"] button[data-baseweb="tab"] {{
        background-color: var(--bg-card) !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        margin-right: 12px !important;
        margin-top: 5px !important;
        margin-bottom: 15px !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 2px 4px var(--shadow-color) !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }}
    
    [data-testid="stTabs"] button[data-baseweb="tab"] p {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px var(--shadow-color-hover) !important;
    }}
    
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
    }}
    
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {{
        color: #ffffff !important;
    }}

    /* Hide the default underline of Streamlit tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        border-bottom: none !important;
        gap: 0px !important;
    }}
    
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    /* Professional Popover Dropdown Styling */
    div[data-testid="stPopoverBody"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px var(--shadow-color-hover) !important;
        padding: 15px !important;
    }}
    
    /* Make buttons inside popover look like clean menu items */
    div[data-testid="stPopoverBody"] .stButton > button {{
        border: none !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 15px !important;
        background-color: transparent !important;
        color: var(--text-primary) !important;
        margin-bottom: 5px !important;
        width: 100% !important;
    }}
    
    div[data-testid="stPopoverBody"] .stButton > button:hover {{
        background-color: var(--bg-primary) !important;
        color: var(--accent-color) !important;
        transform: translateX(5px) !important; /* Subtle slide effect */
        box-shadow: none !important;
        filter: none !important;
    }}

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {{
        border-radius: 8px !important;
        transition: transform 0.2s ease, filter 0.2s ease !important;
        border: 1px solid var(--accent-color) !important;
        background-color: transparent !important;
        color: var(--accent-color) !important;
    }}
    
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        transform: scale(1.02) !important;
        background-color: var(--accent-color) !important;
        color: #fff !important;
        filter: brightness(1.1) !important;
    }}
    
    /* Primary buttons */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"] {{
        background-color: var(--accent-color) !important;
        color: #fff !important;
    }}
    
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {{
        background-color: var(--accent-color) !important;
        box-shadow: 0 4px 10px var(--shadow-color-hover) !important;
    }}

    </style>
    """
    return css

def apply_theme():
    # If no theme is selected yet in session state, default to Sunset Glow
    if "ui_theme" not in st.session_state:
        st.session_state["ui_theme"] = "Sunset Glow (Light)"
        
    theme_css = get_theme_css(st.session_state["ui_theme"])
    st.markdown(theme_css, unsafe_allow_html=True)
