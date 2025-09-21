import streamlit as st
import fastf1
import pandas as pd


class SessionManager:
    # Handles F1 session loading and driver management for pole position analysis

    def __init__(self):
        # ---- Initialise FastF1 cache on first use ----
        self._initialise_fastf1_cache()

    @st.cache_resource
    def _initialise_fastf1_cache(_self):
        # Enable FastF1 cache so that data loads faster after first request
        fastf1.Cache.enable_cache("f1_cache")
        return True

    @st.cache_data
    def get_available_events_for_year(_self, year: int):
        # Get list of available Grand Prix events for a specific year
        try:
            # get season schedule using FastF1
            schedule = fastf1.get_event_schedule(year)
            if schedule is None or schedule.empty:
                return [], f"No events found for {year}"
            
            # Extract unique event names
            events = schedule['EventName'].dropna().unique().tolist()

            # Remove testing / pre-season
            blacklist = ["Pre-Season", "Pre Season", "Testing", "Test"]
            events = [
                e for e in events
                if not any(bad.lower() in e.lower() for bad in blacklist)
            ]
            
            # Sort alphabetically
            events = sorted([event for event in events if event])
            
            return events, f"Found {len(events)} events for {year}"
        except Exception as e:
            return [], f"Error getting events for {year}: {str(e)}"

    @st.cache_data
    def load_qualifying_session(_self, gp_name: str, year: int):
        # Load F1 qualifying session data for a given year 
        try:
            session = fastf1.get_session(year, gp_name, "Q")  # Q = qualifying
            session.load()  # Load timing and lap data
            return session, f"✅ Successfully loaded {year} {gp_name} Qualifying"
        except Exception as e:
            return None, f"❌ Error loading session: {str(e)}"

    def get_pole_position_driver(self, session):
        # Identify pole position
        if session is None:
            return None, "No session loaded"
        
        try:
            results = session.results
            if results is None or results.empty:
                return None, "No qualifying results available"
            
            pole_driver = results[results['Position'] == 1]
            if pole_driver.empty:
                return None, "No pole position data found"
            
            driver_code = pole_driver['Abbreviation'].iloc[0]  
            driver_name = pole_driver['FullName'].iloc[0]      # full name of driver 
            
            return driver_code, f"Pole position: {driver_name} ({driver_code})"
            
        except Exception as e:
            return None, f"Error finding pole position: {e}"

    def get_available_drivers(self, session):
        # Return list of drivers who took part in the session
        if session is None:
            return []
        try:
            drivers = session.laps["Driver"].unique()
            return sorted([d for d in drivers if str(d) != "nan"])
        except Exception as e:
            print(f"Error getting drivers: {e}")
            return []

    def get_available_years(self):
        # Get list of 2018 to 2025 
        import datetime
        current_year = datetime.datetime.now().year
        return list(range(2018, current_year + 1))

    def get_session_info(self, session):
        # Extract basic metadata about the session i.e. event name, session name, date, total laps, year
        if session is None:
            return {}
        try:
            return {
                "event_name": session.event["EventName"],
                "session_name": session.name,
                "date": session.date,
                "total_laps": len(session.laps),
                "year": session.event.get("EventDate", pd.NaT).year if hasattr(session, 'event') else None,
            }
        except Exception as e:
            print(f"Error getting session info: {e}")
            return {}

    def get_drivers_and_teams_for_session(self, session):
        # Get driver and team information for the session
        
        if session is None:
            return {}
        try:
            driver_info = {}

            # Use official results first
            if hasattr(session, 'results') and session.results is not None:
                results = session.results
                for _, driver in results.iterrows():
                    if pd.notna(driver.get('Abbreviation')):
                        driver_info[driver['Abbreviation']] = {
                            'full_name': driver.get('FullName', 'Unknown'),
                            'team': driver.get('TeamName', 'Unknown Team'),
                            'grid_position': driver.get('GridPosition', 'N/A'),
                            'position': driver.get('Position', 'N/A')
                        }
            
            # If no results, fall back to lap data
            if not driver_info and hasattr(session, 'laps'):
                unique_drivers = session.laps[['Driver', 'Team']].drop_duplicates()
                for _, row in unique_drivers.iterrows():
                    if pd.notna(row['Driver']):
                        driver_info[row['Driver']] = {
                            'full_name': row['Driver'],
                            'team': row.get('Team', 'Unknown Team'),
                            'grid_position': 'N/A',
                            'position': 'N/A'
                        }
            
            return driver_info
        except Exception as e:
            print(f"Error getting driver info: {e}")
            return {}

    def validate_session(self, session) -> bool:
        # Validate that a session has been loaded properly
        # Ensures laps dataframe exists and is non-empty
        if session is None:
            return False
        try:
            return hasattr(session, "laps") and not session.laps.empty
        except Exception:
            return False
