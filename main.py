import streamlit as st
from session_manager import SessionManager
from data_analyser import DataAnalyser
from chart_creator import ChartCreator
from ui_styler import UIStyler
import pandas as pd
import numpy as np


class F1QualifyingApp:
    # ---- Main app ----
    
    def __init__(self):
        # Initialise helper classes
        self.session_manager = SessionManager()
        self.data_analyser = DataAnalyser()
        self.chart_creator = ChartCreator()
        self.ui_styler = UIStyler()
        
        # Configure Streamlit page + session state
        self._setup_page_config()
        self._initialise_session_state()

    def _setup_page_config(self):
        # Configure Streamlit page settings
        st.set_page_config(
            page_title = "Formula 1 Pole Position Qualifying Analysis",
            page_icon = "🏁",
            layout = "wide",
            initial_sidebar_state = "expanded"   # Sidebar always open
        )

    def _initialise_session_state(self):
        # Initialise variables
        session_vars = [
            'current_session', 'session_name',
            'current_driver', 'pole_lap',
            'telemetry', 'track_map', 'last_session_key',
            'selected_year', 'available_gps', 'gp_load_message'
        ]

        # Ensure variables exist
        for var in session_vars:
            if var not in st.session_state:
                st.session_state[var] = None

        if 'driver_info' not in st.session_state:
            st.session_state.driver_info = {}

        # Default to current year if no year selected
        if st.session_state.selected_year is None:
            import datetime
            st.session_state.selected_year = datetime.datetime.now().year

        if st.session_state.available_gps is None:
            st.session_state.available_gps = []

    # ---------------- Sidebar ----------------
    def run(self):
        # Run the Streamlit app
        self.render_sidebar()
        self.render_main_content()
    
    def render_sidebar(self):
        # Render sidebar controls for session selection
        with st.sidebar:
            st.header("Session Selection")

            # Select year
            available_years = self.session_manager.get_available_years()
            st.write("")
            selected_year = st.selectbox(
                "Select Year", 
                available_years, 
                index = max(0, len(available_years) - 1),  # default to latest year
                help = f"Data available from {min(available_years)} to {max(available_years)}."
            )

            # Load events for selected year
            if ("last_year" not in st.session_state or 
                st.session_state.last_year != selected_year or
                not st.session_state.available_gps):
                
                with st.spinner(f"Loading Grand Prix events for {selected_year}..."):
                    gps, message = self.session_manager.get_available_events_for_year(selected_year)
                    st.session_state.available_gps = gps
                    st.session_state.gp_load_message = message
                    st.session_state.last_year = selected_year
                    st.session_state.selected_year = selected_year

                    # Reset state when year changes
                    st.session_state.current_driver = None
                    st.session_state.pole_lap = None
                    st.session_state.telemetry = None
                    st.session_state.current_session = None
                    st.session_state.track_map = None
                    st.session_state.last_session_key = None
                    st.session_state.driver_info = {}

            if st.session_state.available_gps:
                st.success(st.session_state.gp_load_message)
                
                # Select Grand Prix
                selected_gp = st.selectbox(
                    "Select Grand Prix", 
                    st.session_state.available_gps, 
                    index = 0,
                    help = f"Available Grand Prix events for {selected_year}"
                )
                
                # Reset state if GP changes
                if ("last_gp" not in st.session_state or 
                    st.session_state.last_gp != selected_gp):
                    
                    st.session_state.last_gp = selected_gp
                    st.session_state.current_driver = None
                    st.session_state.pole_lap = None
                    st.session_state.telemetry = None
                    st.session_state.current_session = None
                    st.session_state.track_map = None
                    st.session_state.last_session_key = None
                    st.session_state.driver_info = {}

                # Load session controls
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Load Session", type="primary"):
                        self._load_session(selected_gp, selected_year)
                with col2:
                    if st.button("Reload", type="secondary"):
                        self._load_session(selected_gp, selected_year)

                # If session is loaded, show analysis options
                if st.session_state.current_session is not None:
                    self._render_pole_position_analysis()
                    
            else:
                st.error(st.session_state.gp_load_message or f"No Grand Prix events found for {selected_year}")
                st.info("Try selecting a different year.")

    def _load_session(self, gp_name, year):
        # Load the qualifying session for a given GP + year
        with st.spinner(f"Loading {year} {gp_name} Qualifying sessions..."):
            session, message = self.session_manager.load_qualifying_session(gp_name, year)

            if session:
                # Save session data into state
                st.session_state.current_session = session
                st.session_state.session_name = f"{year} {gp_name} Qualifying"
                st.session_state.current_driver = None
                st.session_state.pole_lap = None
                st.session_state.telemetry = None
                st.session_state.track_map = None
                st.session_state.last_session_key = None

                st.session_state.driver_info = self.session_manager.get_drivers_and_teams_for_session(session)
                
                st.success(message)
            else:
                st.error(message)

    # ---------------- Analysis Methods ----------------
    def _analyse_pole_position_lap(self, driver_code):
        # Analyse pole-sitter’s lap and extract telemetry 
        session_key = f"{st.session_state.selected_year}_{st.session_state.session_name}_{driver_code}"

        if st.session_state.get("last_session_key") != session_key:
            with st.spinner(f"Analysing {driver_code}'s qualifying lap..."):
                pole_lap, telemetry, message = self.data_analyser.get_pole_position_lap(
                    st.session_state.current_session, driver_code
                )

                if pole_lap is not None:
                    st.session_state.current_driver = driver_code
                    st.session_state.pole_lap = pole_lap
                    st.session_state.telemetry = telemetry

                    # Ensure distance column exists
                    if "Distance" not in st.session_state.telemetry.columns:
                        st.session_state.telemetry = st.session_state.telemetry.copy()
                        st.session_state.telemetry["Distance"] = range(len(st.session_state.telemetry))

                    # Build track map with speed colouring
                    st.session_state.track_map = self.chart_creator.create_track_map_with_sectors(
                        telemetry = st.session_state.telemetry,
                        driver_code = driver_code
                    )

                    st.session_state.last_session_key = session_key
                else:
                    st.error(message)
        else:
            st.info("Information already provided.")

    def _render_pole_position_analysis(self):
        # Display pole-sitter info + option to analyse their lap
        st.header("Pole Position Analysis")
        st.write("")
        
        pole_driver, pole_message = self.session_manager.get_pole_position_driver(st.session_state.current_session)
        
        if pole_driver:
            driver_info = st.session_state.driver_info.get(pole_driver, {})
            full_name = driver_info.get('full_name', pole_driver)
            team = driver_info.get('team', 'Unknown Team')
            
            st.success(f"🏆 **Pole Position**: \n{full_name} ({team})")
            
            if st.button("Analyse Pole Position", type = "primary"):
                self._analyse_pole_position_lap(pole_driver)
                        
        else:
            st.warning(pole_message)
            
            # Allow manual driver selection if pole not detected
            available_drivers = list(st.session_state.driver_info.keys()) if st.session_state.driver_info else self.session_manager.get_available_drivers(st.session_state.current_session)
            
            if available_drivers:
                def format_driver_name(driver_code):
                    driver_info = st.session_state.driver_info.get(driver_code, {})
                    full_name = driver_info.get('full_name', driver_code)
                    team = driver_info.get('team', 'Unknown')
                    return f"{full_name} ({driver_code}) - {team}"
                
                selected_driver = st.selectbox(
                    "Select Driver", 
                    available_drivers, 
                    index = 0,
                    format_func = format_driver_name
                )
                if st.button("Analyse Driver", type="primary"):
                    self._analyse_pole_position_lap(selected_driver)

    # ---------------- Main Content ----------------
    def render_main_content(self):
        # Main body
        self.ui_styler.apply_custom_css()
        st.markdown('<h1 class="main-header">Pole Position Qualifying Analysis</h1>', unsafe_allow_html=True)

        if st.session_state.current_driver is None:
            self._render_welcome_screen()
        else:
            self._render_analysis_results()
        
        st.write("")

    def _render_welcome_screen(self):
        # intro page
        st.write("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Key Features")
            st.write("")
            st.markdown("""
            - **Historical Coverage**: Analyse pole positions from 2018 onwards. 
            - **Dynamic Calendar**: Automatically loads the correct Grand Prix schedule for each year. 
            - **Driver and Team Info**: Shows accurate driver line-ups and team affiliations for each season. 
            - **Pole Position Focus**: Identifies and analyses pole-winning qualifying laps. 
            - **Telemetry Analysis**: Speed, throttle, brake, gear, longitudinal acceleration, and lateral acceleration. 
            - **Track Visualisation**: Speed-coloured track maps. 
            """)
            
        with col2:
            st.markdown("### What You Can Discover")
            st.write("")
            st.markdown("""
            - How pole positions were won across different eras.
            - Evolution of qualifying performance from 2018 to present.  
            - Driver and team performance in different seasons.
            - Circuit-specific qualifying strategies.
            - Historical comparisons of lap times and driving patterns.
            """)
        
        st.subheader("Getting Started")
        st.write("")
        st.markdown("""
        1. **Select Year**: Choose from 2018 onwards. 
        2. **Choose Grand Prix**: The application automatically loads the correct calendar for your selected year. 
        3. **Load Session**: Access the qualifying session data. 
        4. **Analyse Pole**: The application identifies the pole position winner. 
        """)
        
        st.write("")
        st.info("💡 **Tip**: Different years have different Grand Prix!")

    def _render_analysis_results(self):
        # Render all results once a lap has been analysed
        driver = st.session_state.current_driver
        pole_lap = st.session_state.pole_lap
        telemetry = st.session_state.telemetry

        st.subheader("ANALYSIS")

        self._render_basic_lap_info(pole_lap)
        self._render_performance_metrics(telemetry)
        self._render_lap_details(pole_lap)

        st.subheader("VISUAL ANALYSIS")
        st.write("")

        if st.session_state.track_map:
            st.plotly_chart(st.session_state.track_map, use_container_width=True, key="track_map")

        telemetry_chart = self.chart_creator.create_telemetry_chart(telemetry, driver)
        if telemetry_chart:
            st.plotly_chart(telemetry_chart, use_container_width=True, key="telemetry_chart")

    # ---------------- Helpers ----------------
    def _format_time(self, td):
        # Format sector times as mm:ss.mmm
        if pd.isna(td):
            return "N/A"
        total_seconds = td.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"

    def _render_basic_lap_info(self, pole_lap):
        # Show basic lap info
        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """
        col1, col2, col3 = st.columns(3)
        
        driver_code = pole_lap['Driver']
        driver_info = st.session_state.driver_info.get(driver_code, {})
        full_driver_name = driver_info.get('full_name', driver_code)
        
        with col1:
            gp_name = st.session_state.get("session_name", "Unknown GP")
            st.markdown(custom_metric("Event", gp_name), unsafe_allow_html=True)
            
        with col2:
            st.markdown(custom_metric("Driver", full_driver_name), unsafe_allow_html=True)

        with col3:
            st.markdown(custom_metric("Team", pole_lap['Team']), unsafe_allow_html=True)

        st.write("")
        st.write("")

    def _render_performance_metrics(self, telemetry):
        # Display driving metrics and patterns chart
        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """
        
        metrics = self.data_analyser.calculate_performance_metrics(telemetry)
                    
        if metrics:
            st.subheader("PERFORMANCE METRICS")

            left_col, right_col = st.columns([1, 1])
        
            with left_col:
                col1, col2, col3 = st.columns(3)
            
                def fmt(val, suffix=""):
                    return f"{val:.2f}{suffix}" if val is not None else "N/A"
            
                with col1:
                    st.markdown(custom_metric("Max Acceleration", fmt(metrics.get("max_accel_g"), " g")), unsafe_allow_html=True)
                    st.markdown(custom_metric("Maximum Speed", fmt(metrics.get("max_speed"), " km/h")), unsafe_allow_html=True)
            
                with col2:
                    st.markdown(custom_metric("Max Braking", fmt(metrics.get("max_braking_g"), " g")), unsafe_allow_html=True)
                    st.markdown(custom_metric("Minimum Speed", fmt(metrics.get("min_speed"), " km/h")), unsafe_allow_html=True)
                    
                with col3:
                    st.markdown(custom_metric("Max Lateral Force", fmt(metrics.get("max_lateral_g"), " g")), unsafe_allow_html=True)
        
            with right_col:
                patterns_chart = self.chart_creator.create_driving_patterns_chart(metrics, st.session_state.current_driver)
                if patterns_chart:
                    st.plotly_chart(patterns_chart, use_container_width=True, key="patterns_chart")

    def _render_lap_details(self, pole_lap):
        # Show detailed lap breakdown: lap time, sectors, compound 
        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: white; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """
        
        st.subheader("LAP DETAILS")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1: 
            st.markdown(custom_metric("Lap Time", self._format_time(pole_lap['LapTime'])), unsafe_allow_html=True)

        with col2: 
            st.markdown(custom_metric("Sector 1", self._format_time(pole_lap['Sector1Time'])), unsafe_allow_html=True)

        with col3: 
            st.markdown(custom_metric("Sector 2", self._format_time(pole_lap['Sector2Time'])), unsafe_allow_html=True)

        with col4: 
            st.markdown(custom_metric("Sector 3", self._format_time(pole_lap['Sector3Time'])), unsafe_allow_html=True)

        with col5:
            st.markdown(custom_metric("Compound", pole_lap['Compound']), unsafe_allow_html=True)
        
        st.write("")
        st.write("")


def main():
    app = F1QualifyingApp()
    app.run()


if __name__ == "__main__":
    main()
