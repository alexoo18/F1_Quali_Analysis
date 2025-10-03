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
        self.session_manager = SessionManager()
        self.data_analyser = DataAnalyser()
        self.chart_creator = ChartCreator()
        self.ui_styler = UIStyler()

        self._setup_page_config()
        self._initialise_session_state()

    def _setup_page_config(self):
        st.set_page_config(
            page_title = "Formula 1 Qualifying Laps Analysis",
            page_icon = "🏎️🏁📊",
            layout = "wide",
            initial_sidebar_state = "expanded",
        )

    def _initialise_session_state(self):
        session_vars = [
            "current_session",
            "session_name",
            "last_session_key",
            "selected_year",
            "available_gps",
            "gp_load_message",
            "comparison_mode",
        ]
        
        for var in session_vars:
            if var not in st.session_state:
                st.session_state[var] = None

        # Driver-related
        for var in [
            "driver1",
            "driver2",
            "pole_lap1",
            "pole_lap2",
            "telemetry1",
            "telemetry2",
            "track_map1",
            "track_map2",
        ]:
            if var not in st.session_state:
                st.session_state[var] = None

        if "driver_info" not in st.session_state:
            st.session_state.driver_info = {}
            
        if "comparison_mode" not in st.session_state:
            st.session_state.comparison_mode = False

        if st.session_state.selected_year is None:
            import datetime
            st.session_state.selected_year = datetime.datetime.now().year
            
        if st.session_state.available_gps is None:
            st.session_state.available_gps = []

    # ---------------- Sidebar ----------------
    def run(self):
        self.render_sidebar()
        self.render_main_content()

    def render_sidebar(self):
        with st.sidebar:
            st.header("SESSION SELECTION")

            # Year
            available_years = self.session_manager.get_available_years()
            st.write("")
            selected_year = st.selectbox(
                "Select Year",
                available_years,
                index = max(0, len(available_years) - 1),
                help = f"Data available from {min(available_years)} to {max(available_years)}.",
            )

            # When year changes, reload GP list
            if (
                "last_year" not in st.session_state
                or st.session_state.last_year != selected_year
                or not st.session_state.available_gps
            ):
                with st.spinner(f"Loading Grand Prix events for {selected_year}..."):
                    gps, message = self.session_manager.get_available_events_for_year(
                        selected_year
                    )
                    st.session_state.available_gps = gps
                    st.session_state.gp_load_message = message
                    st.session_state.last_year = selected_year
                    st.session_state.selected_year = selected_year
                    self._reset_driver_state()

            if st.session_state.available_gps:
                st.success(st.session_state.gp_load_message)

                selected_gp = st.selectbox(
                    "Select Grand Prix",
                    st.session_state.available_gps,
                    index = 0,
                    help = f"Available Grand Prix events for {selected_year}",
                )

                if (
                    "last_gp" not in st.session_state
                    or st.session_state.last_gp != selected_gp
                ):
                    st.session_state.last_gp = selected_gp
                    self._reset_driver_state()

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("LOAD SESSION", type = "primary"):
                        self._load_session(selected_gp, selected_year)
                        
                with col2:
                    if st.button("RELOAD", type = "secondary"):
                        self._load_session(selected_gp, selected_year)

                if st.session_state.current_session is not None:
                    self._render_analysis_options()
                    
            else:
                st.error(
                    st.session_state.gp_load_message
                    or f"No Grand Prix events found for {selected_year}"
                )
                st.info("Try selecting a different year.")

    def _reset_driver_state(self):
        st.session_state.driver1 = None
        st.session_state.driver2 = None
        st.session_state.pole_lap1 = None
        st.session_state.pole_lap2 = None
        st.session_state.telemetry1 = None
        st.session_state.telemetry2 = None
        st.session_state.track_map1 = None
        st.session_state.track_map2 = None
        st.session_state.current_session = None
        st.session_state.last_session_key = None
        st.session_state.driver_info = {}
        st.session_state.comparison_mode = False

    def _load_session(self, gp_name, year):
        with st.spinner(f"Loading {year} {gp_name} Qualifying sessions..."):
            session, message = self.session_manager.load_qualifying_session(
                gp_name, year
            )
            
            if session:
                st.session_state.current_session = session
                st.session_state.session_name = f"{year} {gp_name} Qualifying"
                self._reset_driver_state()
                st.session_state.current_session = session
                st.session_state.driver_info = (
                    self.session_manager.get_drivers_and_teams_for_session(session)
                )
                st.success(message)
            else:
                st.error(message)

    # ---------------- Analysis Options ----------------
    def _render_analysis_options(self):
        # st.header("ANALYSIS MODE")
        # st.write("")

        # pole_driver, pole_message = self.session_manager.get_pole_position_driver(
        #     st.session_state.current_session
        # )

        # analysis_mode = st.radio(
        #     "Select Analysis Mode",
        #     ["Analyse Pole Position", "Compare Two Drivers"],
        #     index = 0,
        # )

        # st.write("")

        # if analysis_mode == "Analyse Pole Position":
        #     st.session_state.comparison_mode = False
        #     self._render_single_driver_analysis(pole_driver, pole_message)
        # else:
        #     st.session_state.comparison_mode = True
        #     self._render_custom_comparison_analysis()
        st.header("ANALYSIS MODE")
        st.write("")

        pole_driver, pole_message = self.session_manager.get_pole_position_driver(
            st.session_state.current_session
        )

        analysis_mode = st.radio(
            "Select Analysis Mode",
            ["Analyse Pole Position", "Analyse Specific Driver", "Compare Two Drivers"],
            index=0,
        )

        st.write("")

        if analysis_mode == "Analyse Pole Position":
            st.session_state.comparison_mode = False
            self._render_single_driver_analysis(pole_driver, pole_message)

        elif analysis_mode == "Analyse Specific Driver":
            # single driver flow, but user chooses who
            st.session_state.comparison_mode = False
            self._render_manual_driver_select(1)

        else:  # Compare Two Drivers
            st.session_state.comparison_mode = True
            self._render_custom_comparison_analysis()

    def _render_single_driver_analysis(self, pole_driver, pole_message):
        if pole_driver:
            driver_info = st.session_state.driver_info.get(pole_driver, {})
            full_name = driver_info.get("full_name", pole_driver)
            team = driver_info.get("team", "Unknown Team")
            st.success(f"🏆 **Pole Position**: {full_name} ({team})")
            if st.button("ANALYSE POLE POSITION", type = "primary"):
                self._analyse_single_driver(pole_driver, 1)
        else:
            st.warning(pole_message)
            self._render_manual_driver_select(1)

    def _render_custom_comparison_analysis(self):
        available_drivers = (
            list(st.session_state.driver_info.keys())
            if st.session_state.driver_info
            else []
        )
        
        if not available_drivers:
            return

        def format_driver_name(driver_code):
            info = st.session_state.driver_info.get(driver_code, {})
            full_name = info.get("full_name", driver_code)
            team = info.get("team", "Unknown")
            position = info.get("position", "N/A")
            if position != "N/A" and position is not None:
                try:
                    position = int(position)
                except (ValueError, TypeError):
                    pass
            return f"P{position} -- {driver_code} ({team})"

        col1, col2 = st.columns(2)
        with col1:
            driver1 = st.selectbox(
                "Select Driver 1",
                available_drivers,
                format_func = format_driver_name,
                key = "driver1_select",
            )
            
        with col2:
            driver2 = st.selectbox(
                "Select Driver 2",
                available_drivers,
                format_func = format_driver_name,
                key = "driver2_select",
                index = min(1, len(available_drivers) - 1),
            )

        st.write("")
        
        if st.button("COMPARE SELECTED DRIVERS", type = "primary", use_container_width = True):
            if driver1 == driver2:
                st.warning("⚠️ Please select two different drivers")
            else:
                with st.spinner("Loading comparison data..."):
                    self._analyse_single_driver(driver1, 1)
                    self._analyse_single_driver(driver2, 2)

    def _render_manual_driver_select(self, driver_num):
        available = (
            list(st.session_state.driver_info.keys())
            if st.session_state.driver_info
            else []
        )
        
        if not available:
            return

        def format_driver_name(driver_code):
            info = st.session_state.driver_info.get(driver_code, {})
            full_name = info.get("full_name", driver_code)
            team = info.get("team", "Unknown")
            return f"{driver_code} ({team})"

        selected_driver = st.selectbox(
            "Select Driver",
            available,
            format_func = format_driver_name,
            key = f"manual_select_{driver_num}",
        )
        
        if st.button("ANALYSE DRIVER", type = "primary"):
            self._analyse_single_driver(selected_driver, driver_num)

    # ---------------- Analysis Methods ----------------
    def _analyse_single_driver(self, driver_code, driver_num):
        with st.spinner(f"Analysing {driver_code}'s qualifying lap..."):
            pole_lap, telemetry, message = self.data_analyser.get_pole_position_lap(
                st.session_state.current_session, driver_code
            )

            if pole_lap is None:
                st.error(message)
                return

            setattr(st.session_state, f"driver{driver_num}", driver_code)
            setattr(st.session_state, f"pole_lap{driver_num}", pole_lap)
            setattr(st.session_state, f"telemetry{driver_num}", telemetry)

            # Ensure Distance exists
            if "Distance" not in telemetry.columns:
                telemetry = telemetry.copy()
                telemetry["Distance"] = range(len(telemetry))
                setattr(st.session_state, f"telemetry{driver_num}", telemetry)

            track_map = self.chart_creator.create_track_map_with_sectors(
                telemetry = telemetry, driver_code = driver_code
            )
            setattr(st.session_state, f"track_map{driver_num}", track_map)

            st.success(f"✅ Loaded data for {driver_code}")

    # ---------------- Main Content ----------------
    def render_main_content(self):
        self.ui_styler.apply_custom_css()
        st.markdown(
            '<h1 class="main-header">Formula 1 Qualifying Lap Analysis</h1>',
            unsafe_allow_html=True,
        )

        if st.session_state.driver1 is None:
            self._render_welcome_screen()
        elif st.session_state.comparison_mode and st.session_state.driver2 is not None:
            self._render_comparison_results()
        else:
            self._render_single_results()

        st.write("")

    def _render_welcome_screen(self):
        
        st.write("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### KEY FEATURES")
            st.write("")
            st.markdown(
                """
            - **Historical Coverage**: Analyse qualifying from 2018 to present
            - **Driver Modes**: Analyse a specific driver or compare any two side-by-side
            - **Dynamic Calendar**: Automatically loads the correct Grand Prix for the selected year
            - **Driver and Team Info**: Accurate season line-ups and team affiliations
            - **Pole Position Analysis**: Detects the pole lap and breaks it down by sector
            - **Telemetry**: Speed, throttle, brake, gear, longitudinal g, and lateral g
            - **Time-Delta Chart**: See exactly where time is gained or lost along the lap
            - **Track Visualisation**: Speed-coloured map plus faster-driver overlays for each section
            """
            )
            
        with col2:
            st.markdown("### WHAT YOU CAN DISCOVER")
            st.write("")
            st.markdown(
                """
            - **Why pole was won**: the decisive corners/micro-sectors and how much each contributed  
            - **Where time is gained/lost**: corner-by-corner **Δ-time** along the lap  
            - **Speed vs. cornering trade-offs**: who is quicker on the straights vs. in low/medium/high-speed turns  
            - **Driving style fingerprints**: throttle/brake traces, minimum speeds, braking intensity, and gear usage  
            - **Car strengths**: traction zones, full-throttle share, and heavy-braking percentage  
            - **Sector strengths**: split times and how they add up to the final gap  
            - **Track overlay**: see exactly where each driver carried more speed on the map  
            - **Year-to-year context**: compare qualifying performance for the same GP across seasons
            """
            )

        st.subheader("GETTING STARTED")
        st.write("")
        st.markdown(
            """
            1. **Select Year** — 2018 to present  
            2. **Choose Grand Prix** — the calendar auto-filters for your selected year  
            3. **Load Session** — fetch qualifying data and drivers  
            4. **Pick Analysis Mode** — **Analyse Pole Position**, **Analyse Specific Driver**, or **Compare Two Drivers**
        """
        )
        
        st.write("")
        st.info("💡 **Tip:** Use **Compare Two Drivers** to see exactly where time was won or lost along the lap.")

    def _render_single_results(self):
        driver = st.session_state.driver1
        pole_lap = st.session_state.pole_lap1
        telemetry = st.session_state.telemetry1

        st.subheader("ANALYSIS")
        self._render_basic_lap_info(pole_lap, driver, 1)

        # single-driver: show metrics + patterns in one block
        self._render_performance_metrics(telemetry, driver, 1)

        self._render_lap_details(pole_lap)

        st.subheader("VISUAL ANALYSIS")
        st.write("")
        if st.session_state.track_map1:
            st.plotly_chart(
                st.session_state.track_map1, use_container_width = True, key = "track_map_single"
            )

        
        figs = [
            self.chart_creator.create_speed_chart(telemetry, driver),
            self.chart_creator.create_throttle_chart(telemetry, driver),
            self.chart_creator.create_brake_chart(telemetry, driver),
            self.chart_creator.create_gear_chart(telemetry, driver),
            self.chart_creator.create_longitudinal_accel_chart(telemetry, driver),
            self.chart_creator.create_lateral_accel_chart(telemetry, driver),
        ]

        # Keep only charts that exist 
        figs = [f for f in figs if f is not None]

        for i, fig in enumerate(figs):
            st.plotly_chart(fig, use_container_width = True, key = f"telemetry_single_{driver}_{i}")

    def _render_comparison_results(self):
        # --- Driver headers ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("DRIVER COMPARISON")
            self._render_basic_lap_info(
                st.session_state.pole_lap1, st.session_state.driver1, 1
            )
        with col2:
            st.subheader("")
            self._render_basic_lap_info(
                st.session_state.pole_lap2, st.session_state.driver2, 2
            )

        st.write("")

        # --- Performance metrics ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("PERFORMANCE COMPARISON")
            self._render_performance_metrics(
                st.session_state.telemetry1, st.session_state.driver1, 1
            )
        with col2:
            st.subheader("")
            self._render_performance_metrics(
                st.session_state.telemetry2, st.session_state.driver2, 2
            )

        # --- Driving patterns ---
        st.write("")
        m1 = st.session_state.get("metrics1")
        m2 = st.session_state.get("metrics2")

        c1, c2 = st.columns(2)
        with c1:
            if m1:
                fig1 = self.chart_creator.create_driving_patterns_chart(
                    m1, st.session_state.driver1
                )
                fig1.update_yaxes(automargin = True)
                fig1.update_layout(margin = dict(l = 0, r = 20, t = 10, b = 10))
                st.plotly_chart(
                    fig1, use_container_width = True, config = {"displayModeBar": False}
                )
        with c2:
            if m2:
                fig2 = self.chart_creator.create_driving_patterns_chart(
                    m2, st.session_state.driver2
                )
                fig2.update_yaxes(automargin = True)
                fig2.update_layout(margin = dict(l = 0, r = 20, t = 10, b = 10))
                st.plotly_chart(
                    fig2, use_container_width = True, config = {"displayModeBar": False}
                )

        # --- Lap details comparison ---
        st.write("")
        st.subheader("LAP TIME BREAKDOWN")
        st.write("")
        self._render_lap_comparison()

        # --- Visual comparison ---
        st.write("")
        st.subheader("VISUAL BREAKDOWN")
        st.write("")

        comparison_map = self.chart_creator.create_comparison_track_map(
            st.session_state.telemetry1,
            st.session_state.telemetry2,
            st.session_state.driver1,
            st.session_state.driver2,
        )
        
        if comparison_map:
            st.plotly_chart(comparison_map, use_container_width = True, key = "comparison_map")

        # Telemetry comparison
        st.write("### TELEMETRY COMPARISON")
        speed_chart = self.chart_creator.create_speed_comparison_chart(
            st.session_state.telemetry1,
            st.session_state.telemetry2,
            st.session_state.driver1,
            st.session_state.driver2,
        ) 
        
        if speed_chart:
            st.plotly_chart(speed_chart, use_container_width = True, key = "speed_comparison")

        throttle_chart = self.chart_creator.create_throttle_comparison_chart(
            st.session_state.telemetry1,
            st.session_state.telemetry2,
            st.session_state.driver1,
            st.session_state.driver2,
        )
        
        if throttle_chart:
            st.plotly_chart(
                throttle_chart, use_container_width = True, key = "throttle_comparison"
            )

        brake_chart = self.chart_creator.create_brake_comparison_chart(
            st.session_state.telemetry1,
            st.session_state.telemetry2,
            st.session_state.driver1,
            st.session_state.driver2,
        )
        
        if brake_chart:
            st.plotly_chart(brake_chart, use_container_width = True, key = "brake_comparison")

        # Delta analysis
        st.write("### TIME DELTA ANALYSIS")
        st.write("")
        delta_chart = self.chart_creator.create_delta_chart(
            st.session_state.telemetry1,
            st.session_state.telemetry2,
            st.session_state.driver1,
            st.session_state.driver2,
        )
        
        if delta_chart:
            st.plotly_chart(delta_chart, use_container_width = True, key = "delta_chart")

    def _render_lap_comparison(self):
        lap1 = st.session_state.pole_lap1
        lap2 = st.session_state.pole_lap2

        def time_to_seconds(td):
            if pd.isna(td):
                return None
            return td.total_seconds()

        def format_delta(seconds, show_sign = True):
            if seconds is None:
                return "N/A"
            if show_sign:
                return f"+{seconds:.3f}s" if seconds > 0 else f"{seconds:.3f}s"
            else:
                return f"{abs(seconds):.3f}s"

        def delta_color(seconds):
            if seconds is None:
                return "#888888"
            return "#00ff41" if seconds < 0 else "#ff1e30"

        lap1_time = time_to_seconds(lap1["LapTime"])
        lap2_time = time_to_seconds(lap2["LapTime"])
        lap_delta = lap2_time - lap1_time if (lap1_time and lap2_time) else None

        st.markdown(
            f"""
        <div style="border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; text-align: center;">
                <div>
                    <div style="color: #888888; font-size: 0.9rem; margin-bottom: 0.5rem;">{st.session_state.driver1}</div>
                    <div style="color: #444444; font-size: 2rem; font-weight: bold;">{self._format_time(lap1['LapTime'])}</div>
                </div>
                <div>
                    <div style="color: #888888; font-size: 0.9rem; margin-bottom: 0.5rem;">{st.session_state.driver2}</div>
                    <div style="color: #444444; font-size: 2rem; font-weight: bold;">{self._format_time(lap2['LapTime'])}</div>
                    <div style="color: {delta_color(lap_delta)}; font-size: 1.2rem; margin-top: 0.3rem;">{format_delta(lap_delta)}</div>
                </div>
                <div>
                    <div style="color: #888888; font-size: 0.9rem; margin-bottom: 0.5rem;">Faster Driver</div>
                    <div style="color: #444444; font-size: 2rem; font-weight: bold;">{st.session_state.driver1 if lap_delta and lap_delta > 0 else st.session_state.driver2}</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html = True,
        )

        st.markdown(
            f"""<h3 style="color: #dddddd; margin-top: 2rem; margin-bottom: 1rem;">SECTOR COMPARISON</h3>""",
            unsafe_allow_html = True,
        )

        st.markdown(
            f"""
        <div style="display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr; gap: 1rem; 
                    padding: 1rem; border-radius: 5px 5px 0 0;">
            <div style="color: #888888; font-size: 0.9rem; font-weight: bold;">Sector</div>
            <div style="color: #888888; font-size: 0.9rem; font-weight: bold; text-align: center;">{st.session_state.driver1}</div>
            <div style="color: #888888; font-size: 0.9rem; font-weight: bold; text-align: center;">{st.session_state.driver2}</div>
            <div style="color: #888888; font-size: 0.9rem; font-weight: bold; text-align: center;">Faster Driver</div>
            <div style="color: #888888; font-size: 0.9rem; font-weight: bold; text-align: center;">Time Gap (vs faster driver)</div>
        </div>
        """,
            unsafe_allow_html = True,
        )

        sectors = ["Sector1Time", "Sector2Time", "Sector3Time"]
        sector_names = ["1", "2", "3"]

        for i, (sector, name) in enumerate(zip(sectors, sector_names)):
            s1_time = time_to_seconds(lap1[sector])
            s2_time = time_to_seconds(lap2[sector])
            sector_delta = s2_time - s1_time if (s1_time and s2_time) else None

            faster_driver = (
                st.session_state.driver1 if sector_delta and sector_delta > 0 else st.session_state.driver2
            )

            s1_formatted = f"{s1_time:.3f}" if s1_time else "N/A"
            s2_formatted = f"{s2_time:.3f}" if s2_time else "N/A"

            st.markdown(
                f"""
            <div style="display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr; gap: 1rem; 
                        padding: 1rem; background: #f0f0f0; 
                        border-left: 3px solid {('#00ff41' if (sector_delta is not None and sector_delta < 0) else '#ff1e30')}">
                <div style="color: #444444; font-size: 1.1rem;">{name}</div>
                <div style="color: #444444; font-size: 1.1rem; text-align: center;">{s1_formatted}s</div>
                <div style="color: #444444; font-size: 1.1rem; text-align: center;">{s2_formatted}s</div>
                <div style="color: #444444; font-size: 1.1rem; font-weight: bold; text-align: center;">{faster_driver if sector_delta else '-'}</div>
                <div style="color: {('#00ff41' if (sector_delta is not None and sector_delta < 0) else '#ff1e30')}; font-size: 1.1rem; font-weight: bold; text-align: center;">
                    { (f"+{abs(sector_delta):.3f}s" if sector_delta else 'N/A') }
                </div>
            </div>
            """,
                unsafe_allow_html = True,
            )
            
            st.write("")

    # ---------------- Helpers ----------------
    def _format_time(self, td):
        if pd.isna(td):
            return "N/A"
        total_seconds = td.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"

    def _render_basic_lap_info(self, pole_lap, driver_code, driver_num):
        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: #444444; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """

        info = st.session_state.driver_info.get(driver_code, {})
        full_driver_name = info.get("full_name", driver_code)
        position = info.get("position", "N/A")

        if position == "N/A" or position is None:
            position_label = "Position Unknown"
        else:
            try:
                pos_int = int(position)
                position_label = "P1" if pos_int == 1 else f"P{pos_int}"
            except (ValueError, TypeError):
                position_label = f"P{position}"

        if st.session_state.comparison_mode:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(custom_metric("Driver", full_driver_name), unsafe_allow_html = True)
            with col2:
                st.markdown(custom_metric("Team", pole_lap["Team"]), unsafe_allow_html = True)
            with col3:
                st.markdown(custom_metric("Position", position_label), unsafe_allow_html = True)
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                gp_name = st.session_state.get("session_name", "Unknown GP")
                st.markdown(custom_metric("Event", gp_name), unsafe_allow_html = True)
            with col2:
                st.markdown(custom_metric("Driver", full_driver_name), unsafe_allow_html = True)
            with col3:
                st.markdown(custom_metric("Team", pole_lap["Team"]), unsafe_allow_html = True)

        st.write("")

    def _render_performance_metrics(self, telemetry, driver_code, driver_num, show_patterns=None, show_heading=None):
        
        # --- Renders metric cards ---
        
        # Defaults driven by comparison mode
        if show_patterns is None:
            show_patterns = not st.session_state.comparison_mode
            
        if show_heading is None:
            show_heading = not st.session_state.comparison_mode

        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: #444444; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """
        metrics = self.data_analyser.calculate_performance_metrics(telemetry)
        st.session_state[f"metrics{driver_num}"] = metrics  # cache for later

        if not metrics:
            return

        if show_heading:
            st.subheader("PERFORMANCE METRICS")

        def fmt(val, suffix = ""):
            return f"{val:.2f}{suffix}" if val is not None else "N/A"

        # Layout: if showing patterns (single-driver), use two columns (cards + chart)
        # Otherwise (compare mode), use full width for the three card columns
        if show_patterns:
            left_col, right_col = st.columns([1, 1])
            with left_col:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(custom_metric("Max Acceleration", fmt(metrics.get("max_accel_g"), " g")), unsafe_allow_html = True)
                    st.markdown(custom_metric("Maximum Speed", fmt(metrics.get("max_speed"), " km/h")), unsafe_allow_html = True)
                with c2:
                    st.markdown(custom_metric("Max Braking", fmt(metrics.get("max_braking_g"), " g")), unsafe_allow_html = True)
                    st.markdown(custom_metric("Minimum Speed", fmt(metrics.get("min_speed"), " km/h")), unsafe_allow_html = True)
                with c3:
                    st.markdown(custom_metric("Max Lateral Force", fmt(metrics.get("max_lateral_g"), " g")), unsafe_allow_html = True)

            with right_col:
                patterns_chart = self.chart_creator.create_driving_patterns_chart(metrics, driver_code)
                if patterns_chart:
                    patterns_chart.update_yaxes(automargin = True)
                    patterns_chart.update_layout(margin = dict(l = 0, r = 10, t = 10, b = 10), height = 220)
                    st.plotly_chart(patterns_chart, use_container_width = True, config = {"displayModeBar": False})
        else:
            # compare mode
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(custom_metric("Max Acceleration", fmt(metrics.get("max_accel_g"), " g")), unsafe_allow_html = True)
                st.markdown(custom_metric("Maximum Speed", fmt(metrics.get("max_speed"), " km/h")), unsafe_allow_html = True)
            with c2:
                st.markdown(custom_metric("Max Braking", fmt(metrics.get("max_braking_g"), " g")), unsafe_allow_html = True)
                st.markdown(custom_metric("Minimum Speed", fmt(metrics.get("min_speed"), " km/h")), unsafe_allow_html = True)
            with c3:
                st.markdown(custom_metric("Max Lateral Force", fmt(metrics.get("max_lateral_g"), " g")), unsafe_allow_html = True)

    def _render_lap_details(self, pole_lap):
        def custom_metric(label, value):
            return f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
                <div style="color: #888888; font-size: 0.8rem; margin-bottom: 0.2rem;">{label}</div>
                <div style="color: #444444; font-size: 1.5rem; font-weight: bold;">{value}</div>
            </div>
            """

        st.subheader("LAP DETAILS")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(custom_metric("Lap Time", self._format_time(pole_lap["LapTime"])), unsafe_allow_html = True)
        with col2:
            st.markdown(custom_metric("Sector 1", self._format_time(pole_lap["Sector1Time"])), unsafe_allow_html = True)
        with col3:
            st.markdown(custom_metric("Sector 2", self._format_time(pole_lap["Sector2Time"])), unsafe_allow_html = True)
        with col4:
            st.markdown(custom_metric("Sector 3", self._format_time(pole_lap["Sector3Time"])), unsafe_allow_html = True)
        with col5:
            st.markdown(custom_metric("Compound", pole_lap["Compound"]), unsafe_allow_html = True)

        st.write("")
        st.write("")


def main():
    app = F1QualifyingApp()
    app.run()

if __name__ == "__main__":
    main()
