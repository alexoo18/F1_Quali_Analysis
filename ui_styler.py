import streamlit as st


class UIStyler:
    
    # Handles UI styling and CSS customization for the F1 Pole Position application.
    # Provides a consistent dark-themed interface with gold/red F1 accents.
    

    def __init__(self):
        # Standardized F1 color palette
        self.f1_colors = {
            'primary_red': '#ff1e30',
            'secondary_red': '#dc143c',
            'pole_gold': '#ffd700',      # Gold accent for pole position
            'white': '#ffffff',
            'dark_grey': '#1e1e1e',
            'medium_grey': '#2d2d2d',
            'light_grey': '#333333',
            'background_dark': '#0e1117',
            'success_green': '#00ff41',
            'warning_yellow': '#ffff00',
            'error_red': '#ff073a'
        }

    def apply_custom_css(self):
        
        # Custom CSS into the Streamlit app to override default styling.
        
        css_styles = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
            
            /* === Global Text Colors === */
            .stMarkdown, .stMarkdown p, .stMarkdown li, .stAlert p,
            .stSelectbox label, .stSelectbox div[data-baseweb="select"],
            .stRadio label, .stCheckbox label, p, span {{
                color: #888888 !important;   
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: #dddddd !important;   /* Bright white headers */
            }}
            
            /* === H1/Main Header === */
            .main-header {{
                font-family: 'Orbitron', monospace;
                font-size: 2.5rem;
                font-weight: 900;
                text-align: center;
                color: #888888 !important;
                margin-bottom: 2rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                border-bottom: none !important;
                background: linear-gradient(45deg, #888888, {self.f1_colors['pole_gold']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            /* === H2, H3 with underline accent === */
            h2, h3, .stSubheader {{
                color: #888888 !important;
                border-bottom: 2px solid {self.f1_colors['primary_red']} !important;
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
            
            /* === Metrics === */
            [data-testid="metric-container"] * {{
                color: #f5f5f5 !important;
            }}
            [data-testid="metric-container"] > div:last-child {{
                color: {self.f1_colors['white']} !important;
                font-size: 1.5rem !important;
                font-weight: bold !important;
            }}
        
            /* === Global App Background === */
            .stApp {{
                font-family: 'Inter', sans-serif;
                background-color: {self.f1_colors['background_dark']};
            }}
            
            /* === Sidebar === */
            section[data-testid="stSidebar"] {{
                background-color: {self.f1_colors['dark_grey']};
                border-right: 3px solid {self.f1_colors['primary_red']};
                box-shadow: 2px 0 10px rgba(255, 215, 0, 0.1);
            }}
            
            /* === Buttons === */
            .stButton > button {{
                font-family: 'Orbitron', monospace;
                font-weight: 600;
                letter-spacing: 1px;
                background: {self.f1_colors['primary_red']};
                border: none;
                border-radius: 5px;
                color: {self.f1_colors['white']};
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .stButton > button:before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }}
            
            .stButton > button:hover:before {{
                left: 100%;
            }}
            
            .stButton > button:hover {{
                background: linear-gradient(45deg, {self.f1_colors['secondary_red']}, {self.f1_colors['pole_gold']});
                box-shadow: 0 4px 15px rgba(255, 30, 48, 0.4);
                transform: translateY(-2px);
            }}
            
            /* === Metric Cards === */
            [data-testid="metric-container"] {{
                background: {self.f1_colors['dark_grey']};
                border: 1px solid {self.f1_colors['light_grey']};
                border-left: 3px solid {self.f1_colors['pole_gold']};
                border-radius: 8px;
                padding: 1rem;
                transition: all 0.3s ease;
            }}
            
            [data-testid="metric-container"]:hover {{
                border-left: 3px solid {self.f1_colors['primary_red']};
                box-shadow: 0 2px 10px rgba(255, 215, 0, 0.1);
            }}
            
            [data-testid="metric-container"] > div {{
                color: {self.f1_colors['white']};
            }}
            
            /* === Sidebar Messages === */
            section[data-testid="stSidebar"] .stSuccess {{
                background: linear-gradient(90deg, rgba(0,255,65,0.1), rgba(255,215,0,0.1));
                border-left: 4px solid {self.f1_colors['pole_gold']};
                padding: 1rem !important;
                margin: 2rem 1rem 1rem 1rem !important;
                font-size: 0.9rem !important;
                width: 100% !important;
                box-sizing: border-box !important;
                color: #f5f5f5 !important;
            }}
            
            section[data-testid="stSidebar"] .stInfo {{
                background: linear-gradient(90deg, rgba(255,30,48,0.1), rgba(255,215,0,0.1));
                border-left: 4px solid {self.f1_colors['primary_red']};
                padding: 1rem !important;
                margin: 0 !important;
                font-size: 0.9rem !important;
                width: 100% !important;
                box-sizing: border-box !important;
                color: #f5f5f5 !important;
            }}
            
            /* === Hide Streamlit Default UI === */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            
            /* === Custom Scrollbar === */
            ::-webkit-scrollbar {{ width: 12px; }}
            ::-webkit-scrollbar-track {{ 
                background: {self.f1_colors['dark_grey']};
                border-radius: 6px;
            }}
            ::-webkit-scrollbar-thumb {{
                background: linear-gradient(180deg, {self.f1_colors['primary_red']}, {self.f1_colors['pole_gold']});
                border-radius: 6px;
                transition: all 0.3s ease;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: linear-gradient(180deg, {self.f1_colors['pole_gold']}, {self.f1_colors['primary_red']});
            }}
            
            /* === Selectbox Styling === */
            .stSelectbox > div > div {{
                background-color: {self.f1_colors['medium_grey']};
                border: 1px solid {self.f1_colors['light_grey']};
                color: #f5f5f5 !important;
            }}
            
            .stSelectbox > div > div:focus-within {{
                border: 1px solid {self.f1_colors['pole_gold']};
                box-shadow: 0 0 0 1px {self.f1_colors['pole_gold']};
            }}
        </style>
        """
        st.markdown(css_styles, unsafe_allow_html=True)
