import streamlit as st

class UIStyler:
    
    # Handles UI styling and CSS customisation for the F1 Pole Position application.

    def __init__(self):
        self.f1_colors = {
            'primary_yellow': '#ffeb99',   # soft light yellow
            'secondary_yellow': '#ffe066', # brighter accent yellow
            'pole_gold': '#c9a24a',        # muted gold
            'white': '#ffffff',
            'medium_grey': '#e0e0e0',
            'dark_text': '#1a1a1a',
            'success_green': '#2ca02c',
            'warning_orange': '#ff9f1c',
            'error_red': '#e63946'
        }

    def apply_custom_css(self):
        css_styles = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

            /* === Set global app background to white === */
            .stApp {{
                background-color: {self.f1_colors['white']} !important;
            }}

            /* === Global Text === */
            .stMarkdown, .stMarkdown p, .stMarkdown li, .stAlert p,
            .stSelectbox label, .stSelectbox div[data-baseweb="select"],
            .stRadio label, .stCheckbox label, p, span {{
                color: {self.f1_colors['dark_text']} !important;   
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: {self.f1_colors['dark_text']} !important;
            }}
            
            /* === H1/Main Header === */
            .main-header {{
                font-family: 'Orbitron', monospace;
                font-size: 2.5rem;
                font-weight: 900;
                text-align: center;
                margin-bottom: 2rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                border-bottom: none !important;
                color: #c9a24a !important; /* muted gold */
            }}
            
            /* === H2, H3 with underline accent === */
            h2, h3, .stSubheader {{
                color: #888888 !important;
                border-bottom: 2px solid {self.f1_colors['primary_yellow']} !important;
                padding-bottom: 0.3rem;
                margin-bottom: 1rem;
                position: relative;
            }}
            
            h2:after, h3:after {{
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                width: 20px;
                height: 2px;
                background: {self.f1_colors['pole_gold']};
            }}
            
            /* === Buttons === */
            .stButton > button {{
                font-family: 'Orbitron', monospace;
                font-weight: 600;
                letter-spacing: 1px;
                background: {self.f1_colors['primary_yellow']};
                border: 1px solid {self.f1_colors['pole_gold']};
                border-radius: 5px;
                color: {self.f1_colors['dark_text']};
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .stButton > button:hover {{
                background: linear-gradient(45deg, {self.f1_colors['secondary_yellow']}, {self.f1_colors['pole_gold']});
                box-shadow: 0 4px 12px rgba(201, 162, 74, 0.2);
                transform: translateY(-2px);
            }}
            
            /* === Sidebar === */
            section[data-testid="stSidebar"] {{
                background-color: {self.f1_colors['white']};
                border-right: 3px solid {self.f1_colors['secondary_yellow']};
                box-shadow: 2px 0 10px rgba(255, 224, 102, 0.2);
            }}

            /* === Sidebar selectboxes: button-style outline for Year & GP === */
            section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
                border: 2px solid {self.f1_colors['pole_gold']};
                border-radius: 10px;
                background: {self.f1_colors['white']};
                min-height: 42px;
                padding: 2px 6px;
                box-shadow: 0 0 0 2px rgba(201,162,74,0.12) inset;
                transition: border-color 120ms ease, box-shadow 120ms ease;
            }}
            section[data-testid="stSidebar"] div[data-baseweb="select"]:hover > div {{
                border-color: {self.f1_colors['secondary_yellow']};
            }}
            section[data-testid="stSidebar"] div[data-baseweb="select"]:focus-within > div {{
                border-color: {self.f1_colors['pole_gold']};
                box-shadow: 0 0 0 3px rgba(201,162,74,0.28);
            }}

            /* === Metric Cards === */
            [data-testid="metric-container"] {{
                background: {self.f1_colors['white']};
                border: 1px solid {self.f1_colors['medium_grey']};
                border-left: 3px solid {self.f1_colors['secondary_yellow']};
                border-radius: 8px;
                padding: 1rem;
                transition: all 0.3s ease;
            }}
            [data-testid="metric-container"]:hover {{
                border-left: 3px solid {self.f1_colors['pole_gold']};
                box-shadow: 0 2px 10px rgba(201, 162, 74, 0.1);
            }}
        </style>
        """
        st.markdown(css_styles, unsafe_allow_html = True)
