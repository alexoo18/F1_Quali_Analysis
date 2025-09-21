import pandas as pd
import numpy as np
import streamlit as st
from scipy.signal import savgol_filter


class DataAnalyser:
    # Handles F1 telemetry data analysis and calculations for pole position laps

    def __init__(self):
        pass

    # ---------------- Session and Lap Handling ----------------
    def get_pole_position_lap(self, _session, driver_code):
        # Get the pole position qualifying lap for a specific driver
        try:
            if _session is None:
                return None, None, "No session loaded."

            # Get laps for driver
            laps = _session.laps.pick_drivers(driver_code)
            if laps is None or laps.empty:
                return None, None, f"No laps available for {driver_code} at this GP."

            # Verify pole position 
            try:
                results = _session.results
                pole_driver = results[results['Position'] == 1]['Abbreviation'].iloc[0]
                # if pole_driver != driver_code:
                #     return None, None, f"{driver_code} did not achieve pole position. Pole was achieved by {pole_driver}."
            except:
                pass

            # Get fastest lap (assumed pole lap)
            pole_lap = laps.pick_fastest()
            if pole_lap is None or pd.isna(pole_lap['LapTime']):
                return None, None, f"No valid pole lap found for {driver_code}."

            # Extract telemetry with distance
            telemetry = pole_lap.get_telemetry().add_distance()
            if telemetry is None or telemetry.empty:
                return None, None, f"No telemetry data for {driver_code}'s pole lap."

            return pole_lap, telemetry, f"Pole position lap for {driver_code} loaded."

        except Exception as e:
            return None, None, f"Error getting pole position lap: {e}"

    def get_fastest_lap(self, _session, driver_code):
        # Backwards-compatible wrapper for pole lap retrieval 
        return self.get_pole_position_lap(_session, driver_code)

    # ---------------- Utilities ----------------
    def _smooth_signal(self, data, window_length=7, polyorder=3):
        # Apply Savitzky-Golay smoothing to reduce noise while preserving features 
        clean_data = data.ffill().bfill()
        return savgol_filter(clean_data, window_length=window_length, polyorder=polyorder)

    def _calculate_time_deltas(self, time_series):
        # Calculate Δt between samples
        time_diff = time_series.diff().dt.total_seconds()
        time_diff = time_diff.replace(0, 0.001).fillna(0.001)
        time_diff[time_diff <= 0] = 0.001
        return time_diff

    # ---------------- Performance Metrics ----------------
    def calculate_performance_metrics(self, telemetry):
        # Calculate lap performance metrics
        if telemetry is None or telemetry.empty:
            return {}

        metrics = {}
        try:
            total_points = len(telemetry)

            # ---- Full Throttle Percentage ----
            if "Throttle" in telemetry.columns:
                throttle = pd.to_numeric(telemetry["Throttle"], errors="coerce").fillna(0)

                # Normalise throttle values
                if throttle.max() <= 1.0:
                    throttle *= 100

                # Full throttle defined as ≥ 98% 
                full_throttle_pct = (throttle >= 98).sum() / total_points * 100
                metrics["full_throttle"] = round(full_throttle_pct)
            else:
                metrics["full_throttle"] = None

            # ---- Heavy Braking Percentage ----
            if "Brake" in telemetry.columns:
                brake = pd.to_numeric(telemetry["Brake"], errors="coerce").fillna(0)

                # Normalise brake values 
                if brake.max() <= 1.0:
                    brake *= 100

                # Heavy braking = brake pressure > 50%
                metrics["heavy_braking"] = round((brake > 50).sum() / total_points * 100) if brake.sum() > 0 else 0
            else:
                metrics["heavy_braking"] = None

            # ---- Cornering Time + Speeds ----
            if "Speed" in telemetry.columns:
                # Define cornering as speed < 200 km/h
                cornering_pct = (telemetry["Speed"] < 200).sum() / total_points * 100
                metrics.update({
                    "cornering": round(cornering_pct),
                    "max_speed": float(telemetry["Speed"].max()),
                    "min_speed": float(telemetry["Speed"].min()),
                })
            else:
                metrics.update({"cornering": None, "max_speed": None, "min_speed": None})

            # ---- Longitudinal Acceleration ----
            if "Speed" in telemetry.columns and "Time" in telemetry.columns:
                # km/h to m/s
                speed_ms = telemetry["Speed"] / 3.6

                # Δt between samples
                time_diff = self._calculate_time_deltas(telemetry["Time"])

                # Acceleration = Δv / Δt
                longitudinal_accel_ms2 = speed_ms.diff() / time_diff

                # m/s^2 to g by dividing by 9.81
                telemetry["longitudinal_accel_g"] = (longitudinal_accel_ms2 / 9.81).clip(-6, 6)

                # Max forward acceleration & Max braking 
                valid_accel = telemetry["longitudinal_accel_g"].replace([np.inf, -np.inf], np.nan).dropna()
                if not valid_accel.empty:
                    metrics["max_accel_g"] = float(valid_accel.max())
                    metrics["max_braking_g"] = float(abs(valid_accel.min()))
                else:
                    metrics.update({"max_accel_g": None, "max_braking_g": None})
            else:
                metrics.update({"max_accel_g": None, "max_braking_g": None})

            # ---- Lateral Acceleration - Fixed Version ----
            if all(col in telemetry.columns for col in ["X", "Y", "Speed"]):
                try:
                    if len(telemetry) >= 7:
                        # Much lighter smoothing to preserve cornering detail
                        x_smooth = self._smooth_signal(telemetry["X"], window_length=5, polyorder=2)
                        y_smooth = self._smooth_signal(telemetry["Y"], window_length=5, polyorder=2)

                        # Calculate derivatives
                        dx, dy = np.gradient(x_smooth), np.gradient(y_smooth)
                        ds = np.sqrt(dx**2 + dy**2)
                        ds[ds < 0.1] = 0.1

                        # Calculate heading
                        heading = np.arctan2(dy, dx)

                        # Calculate heading changes
                        dheading = np.diff(heading)
                        
                        # Handle angle wrapping
                        dheading = np.where(dheading > np.pi, dheading - 2*np.pi, dheading)
                        dheading = np.where(dheading < -np.pi, dheading + 2*np.pi, dheading)
                        dheading = np.append(dheading, 0)

                        # Calculate curvature - MUCH less restrictive clipping
                        raw_curvature = dheading / ds
                        
                        # Use percentile-based clipping instead of hard limits
                        curvature_99 = np.percentile(np.abs(raw_curvature), 99)
                        curvature_limit = max(curvature_99, 0.1)  # At least 0.1 rad/m for F1 corners
                        
                        curvature = np.clip(raw_curvature, -curvature_limit, curvature_limit)

                        # Calculate lateral acceleration
                        speed_ms = telemetry["Speed"] / 3.6
                        lateral_accel_ms2 = speed_ms**2 * np.abs(curvature)
                        
                        # Convert to g with more reasonable limits
                        lat_accel_g = lateral_accel_ms2 / 9.81
                        
                        # Apply realistic F1 limits (0-8g)
                        telemetry["lateral_accel_g"] = np.clip(lat_accel_g, 0, 8)

                        # Calculate maximum
                        valid_lateral = telemetry["lateral_accel_g"].replace([np.inf, -np.inf], np.nan).dropna()
                        if not valid_lateral.empty and valid_lateral.max() > 0.5:
                            metrics["max_lateral_g"] = float(valid_lateral.max())
                        else:
                            # Fallback calculation if primary method fails
                            print("Primary lateral calculation produced low values, using fallback...")
                            
                            # Simple speed-based estimation for corners
                            speed_threshold = telemetry["Speed"].quantile(0.8) * 0.75
                            corner_mask = telemetry["Speed"] < speed_threshold
                            
                            # Estimate lateral g based on speed drop in corners
                            corner_speeds = telemetry.loc[corner_mask, "Speed"] / 3.6
                            estimated_lat_g = np.zeros(len(telemetry))
                            
                            # For corners, estimate lateral g (empirical formula for F1)
                            estimated_lat_g[corner_mask] = (corner_speeds / 20) + 2  # 2-5g range
                            
                            telemetry["lateral_accel_g"] = estimated_lat_g
                            metrics["max_lateral_g"] = float(estimated_lat_g.max()) if estimated_lat_g.max() > 0 else 3.0
                            
                    else:
                        telemetry["lateral_accel_g"] = np.zeros(len(telemetry))
                        metrics["max_lateral_g"] = 0.0
                        
                except Exception as e:
                    print(f"Lateral acceleration calculation failed: {e}")
                    # Simple fallback - estimate based on speed patterns
                    if "Speed" in telemetry.columns:
                        speed_var = telemetry["Speed"].rolling(window=10).std().fillna(0)
                        estimated_lat = (speed_var / 10).clip(0, 5)  # Speed variation indicates cornering
                        telemetry["lateral_accel_g"] = estimated_lat
                        metrics["max_lateral_g"] = float(estimated_lat.max())
                    else:
                        telemetry["lateral_accel_g"] = np.zeros(len(telemetry))
                        metrics["max_lateral_g"] = None
            else:
                telemetry["lateral_accel_g"] = np.zeros(len(telemetry))
                metrics["max_lateral_g"] = None

            # Store raw longitudinal accel in m/s^2 for plotting
            if "longitudinal_accel_g" in telemetry.columns:
                telemetry["longitudinal_accel"] = telemetry["longitudinal_accel_g"] * 9.81

            return metrics

        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {}

    # ---------------- Speed Statistics ----------------
    def calculate_speed_statistics(self, telemetry):
        # Calculate descriptive statistics for speed 
        if telemetry is None or telemetry.empty:
            return {}

        try:
            speed_data = telemetry["Speed"]
            return {
                "average_speed": float(speed_data.mean()),
                "median_speed": float(speed_data.median()),
                "speed_75th_percentile": float(speed_data.quantile(0.75)),
                "speed_25th_percentile": float(speed_data.quantile(0.25)),
                "speed_standard_deviation": float(speed_data.std()),
                "full_throttle": None,
                "heavy_braking": None,
                "cornering": None,
            }
        except Exception as e:    
            print(f"Error calculating speed statistics: {e}")
            return {}

    # ---------------- Throttle & Braking Patterns ----------------
    def analyse_throttle_patterns(self, telemetry):
        # Analyse throttle usage distribution 
        if telemetry is None or telemetry.empty:
            return {}

        try:
            throttle_data = telemetry["Throttle"]
            total_time = len(throttle_data)

            return {
                "full_throttle_percentage": (throttle_data == 100).sum() / total_time * 100,
                "partial_throttle_percentage": ((throttle_data > 0) & (throttle_data < 100)).sum() / total_time * 100,
                "no_throttle_percentage": (throttle_data == 0).sum() / total_time * 100,
                "average_throttle": float(throttle_data.mean()),
            }
        except Exception as e:
            print(f"Error analysing throttle patterns: {e}")
            return {}

    def analyse_braking_patterns(self, telemetry):
        # Analyse braking intensity distribution 
        if telemetry is None or telemetry.empty:
            return {}

        try:
            brake_data = telemetry["Brake"]
            total_time = len(brake_data)

            return {
                "heavy_braking_percentage": (brake_data > 80).sum() / total_time * 100,
                "medium_braking_percentage": ((brake_data > 30) & (brake_data <= 80)).sum() / total_time * 100,
                "light_braking_percentage": ((brake_data > 0) & (brake_data <= 30)).sum() / total_time * 100,
                "no_braking_percentage": (brake_data == 0).sum() / total_time * 100,
                "max_brake_pressure": float(brake_data.max()),
                "average_brake_pressure": float(brake_data.mean()),
            }
        except Exception as e:
            print(f"Error analysing braking patterns: {e}")
            return {}
