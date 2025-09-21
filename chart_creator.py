import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


class ChartCreator:
    def __init__(self):
        
        # Standardised F1 color palette
        
        self.f1_colors = {
            'primary': '#ff1e30',
            'secondary': '#00ff00',
            'brake_color': '#ff0000',
            'background': '#0e1117'
        }

    # ---------------- Ensure distance column ----------------
    
    def _ensure_distance(self, telemetry):
        
        # Ensure that telemetry data has a 'Distance' column.
        # If missing, compute it from (X, Y) coordinates or fall back to index.
        
        if "Distance" in telemetry.columns:
            return telemetry  # Already present

        telemetry = telemetry.copy()
        if "X" in telemetry.columns and "Y" in telemetry.columns:
            dx = telemetry["X"].diff().fillna(0)
            dy = telemetry["Y"].diff().fillna(0)
            telemetry["Distance"] = np.cumsum(np.hypot(dx, dy))
        else:
            telemetry["Distance"] = np.arange(len(telemetry), dtype=float)

        return telemetry

    # ---------------- Driving patterns (horizontal bar chart) ----------------
    
    def create_driving_patterns_chart(self, metrics, driver_code):
        
        # Create a horizontal bar chart showing driving patterns:
        #   - Cornering
        #   - Heavy braking
        #   - Full throttle usage
        
        if not metrics:
            return None

        try:
            categories = ['Cornering', 'Heavy Braking', 'Full Throttle']
            values = [
                int(metrics.get('cornering', 0) or 0),
                int(metrics.get('heavy_braking', 0) or 0),
                int(metrics.get('full_throttle', 0) or 0),
            ]
            colors = ['#ffaa00', '#ff1e30', '#00ff41']  # Orange, red, green

            fig = go.Figure(go.Bar(
                x = values,
                y = categories,
                orientation = 'h',
                marker_color = colors,
                width = 0.5,
            ))

            # Add % labels on bars
            for i, val in enumerate(values):
                fig.add_annotation(
                    x = val + 2,
                    y = i,
                    text = f"{val}%",
                    showarrow = False,
                    font = dict(size = 25, color = 'white'),
                    xanchor = 'left',
                    yanchor = 'middle'
                )

            fig.update_layout(
                margin = dict(l = 120, r = 80, t = 20, b = 20),
                height = 200,
                plot_bgcolor = 'rgba(0,0,0,0)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                showlegend = False,
                bargap = 0.1,
                xaxis = dict(
                    showgrid = False,
                    showticklabels = False,
                    showline = False,
                    zeroline = False,
                    range = [0, max(values) * 1.2]
                ),
                yaxis = dict(
                    showgrid = False,
                    showline = False,
                    tickfont = dict(size = 14, color = '#888888')
                ),
                font = dict(color = '#888888')
            )
            return fig

        except Exception as e:
            print(f"Error creating driving patterns chart: {e}")
            return None

    # ---------------- Track map ----------------
    
    def create_track_map_with_sectors(self, telemetry = None, driver_code = None):
        
        # Create a 2D track map (X, Y positions), color-coded by speed.
    
        if telemetry is None or telemetry.empty:
            return None

        try:
            telemetry = self._ensure_distance(telemetry)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x = telemetry['X'],
                y = telemetry['Y'],
                mode = "markers",
                marker = dict(
                    color = telemetry['Speed'],
                    colorscale = "Turbo",
                    size = 4,
                    colorbar = dict(
                        title = "Speed (km/h)",
                        x = 5,
                        y = 0.5,
                        len = 0.8
                    )
                ),
                name = "Track"
            ))

            fig.update_layout(
                title = dict(
                    text = f"Track Map", 
                    x = 0.5, 
                    xanchor = "center",
                    font = dict(color = '#888888', size = 20)
                ),
                template = "plotly_dark",
                xaxis = dict(visible = False),
                yaxis = dict(visible = False, scaleanchor = "x", scaleratio = 1),
                height = 600,
                font = dict(family = "Arial", size = 12),
                plot_bgcolor = 'rgba(0,0,0,0)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                margin = dict(l = 50, r = 30, t = 70, b = 50)
            )
            return fig

        except Exception as e:
            print(f"Error creating track map: {e}")
            return None

    # ---------------- Telemetry chart ----------------
    
    def create_telemetry_chart(self, telemetry, driver_code):
        
        # Create multi-panel telemetry chart:
        #   - Speed
        #   - Throttle
        #   - Brake
        #   - Gear
        #   - Longitudinal Acceleration
        #   - Lateral Acceleration
        
        self.f1_colors = {
            'primary': '#ff1e30',       # Speed
            'secondary': "#f89fd3",     # Throttle
            'brake_color': "#09f845",   # Brake
            'gear_color': '#800080',    # Gear
            'long_color': '#ffaa00',    # Longitudinal Accel
            'lat_color': '#00aaff',     # Lateral Accel
            'background': '#0e1117'
        }

        if telemetry is None or telemetry.empty:
            return None

        telemetry = self._ensure_distance(telemetry)

        # Detect gear column
        gear_col = None
        for col in telemetry.columns:
            if col.lower() in ['gear', 'ngear']:
                gear_col = col
                break
        has_gear = gear_col is not None

        subplot_titles = ["Speed"]
        if "Throttle" in telemetry.columns: subplot_titles.append("Throttle")
        if "Brake" in telemetry.columns: subplot_titles.append("Brake")
        if has_gear: subplot_titles.append("Gear")
        if "longitudinal_accel_g" in telemetry.columns: subplot_titles.append("Longitudinal Acceleration")
        if "lateral_accel_g" in telemetry.columns: subplot_titles.append("Lateral Acceleration")

        fig = make_subplots(
            rows = len(subplot_titles),
            cols = 1,
            shared_xaxes = True,
            vertical_spacing = 0.12,
            subplot_titles = subplot_titles
        )

        # Style subplot titles
        for ann in fig['layout']['annotations']:
            ann['font'] = dict(size = 20, color = '#888888')
            ann['text'] = f"<b>{ann['text']}</b>"

    # ---------------- Telemetry chart ----------------
    def create_telemetry_chart(self, telemetry, driver_code):
    
        # Create multi-panel telemetry chart:
        #   - Speed
        #   - Throttle
        #   - Brake
        #   - Gear
        #   - Longitudinal Acceleration
        #   - Lateral Acceleration
        
        
        # Standardised F1 color palette
        self.f1_colors = {
            'primary': '#ff1e30',       # Speed
            'secondary': "#f89fd3",     # Throttle
            'brake_color': "#09f845",  # Brake
            'gear_color': '#800080',   # Gear
            'long_color': '#ffaa00',   # Longitudinal Accel
            'lat_color': '#00aaff',    # Lateral Accel
            'background': '#0e1117'
        }

        # Guard clause: no telemetry
        if telemetry is None or telemetry.empty:
            return None

        telemetry = self._ensure_distance(telemetry)

        # Detect gear column ('nGear')
        gear_col = None
        for col in telemetry.columns:
            if col.lower() in ['gear', 'ngear']:
                gear_col = col
                break
        has_gear = gear_col is not None

        # Subplot titles 
        subplot_titles = ["Speed"]
        if "Throttle" in telemetry.columns: subplot_titles.append("Throttle")
        if "Brake" in telemetry.columns: subplot_titles.append("Brake")
        if has_gear: subplot_titles.append("Gear")
        if "longitudinal_accel_g" in telemetry.columns: subplot_titles.append("Longitudinal Acceleration")
        if "lateral_accel_g" in telemetry.columns: subplot_titles.append("Lateral Acceleration")

        # Create figure with shared X-axis
        fig = make_subplots(
            rows = len(subplot_titles),
            cols = 1,
            shared_xaxes = True,
            vertical_spacing = 0.12,
            subplot_titles = subplot_titles
        )

        # Style subplot titles
        for ann in fig['layout']['annotations']:
            ann['font'] = dict(size = 20, color = '#888888')
            ann['text'] = f"<b>{ann['text']}</b>"

        # Track which row we’re working on
        row_idx = 1


        # ==================================================
        # ---- SPEED ----
        # ==================================================
        
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"],
            y = telemetry["Speed"],
            mode = "lines",
            name = "Speed",
            line = dict(color = self.f1_colors['primary'], width = 2),
        ), row = row_idx, col = 1)

        fig.update_yaxes(
            title_text = "km/h",
            tickvals = [0, 100, 200, 300, 400],
            title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
            tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
            showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
            zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.3,
            rangemode = "tozero",
            row = row_idx, col = 1
        )

        fig.update_xaxes(
            title_text = "Distance (m)",
            tickmode = "linear", dtick = 1000, tickformat = ",",
            title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
            tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
            showgrid = False,
            zeroline = False,
            showticklabels = True,
            row = row_idx, col = 1
        )
        row_idx += 1
        

        # ==================================================
        # ---- THROTTLE ----
        # ==================================================
        
        if "Throttle" in telemetry.columns:
            fig.add_trace(go.Scatter(
                x = telemetry["Distance"],
                y = telemetry["Throttle"],
                mode = "lines",
                name = "Throttle",
                line = dict(color = self.f1_colors['secondary'], width = 2),
            ), row = row_idx, col = 1)

            fig.update_yaxes(
                title_text = "%",
                tickvals = [20, 40, 60, 80, 100],   # skip 0 for clarity
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
                zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.5,
                row = row_idx, col = 1
            )

            fig.update_xaxes(
                title_text = "Distance (m)",
                tickmode = "linear", dtick = 1000, tickformat = ",",
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = False,
                zeroline = False,
                showticklabels = True,
                row = row_idx, col = 1
            )
            row_idx += 1
            

        # ==================================================
        # ---- BRAKE ----
        # ==================================================
        if "Brake" in telemetry.columns:
            brake = telemetry["Brake"]
            if brake.dtype == bool:
                brake = brake.astype(int) * 100  # normalise boolean to %
            fig.add_trace(go.Scatter(
                x = telemetry["Distance"],
                y = brake,
                mode = "lines",
                name = "Brake",
                line = dict(color = self.f1_colors['brake_color'], width = 2),
            ), row = row_idx, col = 1)

            fig.update_yaxes(
                title_text = "%",
                tickvals = [20, 40, 60, 80, 100],
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
                zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.5,
                row = row_idx, col = 1
            )

            fig.update_xaxes(
                title_text = "Distance (m)",
                tickmode = "linear", dtick = 1000, tickformat = ",",
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = False,
                zeroline = False,
                showticklabels = True,
                row = row_idx, col = 1
            )
            row_idx += 1


        # ==================================================
        # ---- GEAR ----
        # ==================================================
        
        if has_gear:
            gear_data = pd.to_numeric(telemetry[gear_col], errors = "coerce").fillna(0).astype(int)
            fig.add_trace(go.Scatter(
                x = telemetry["Distance"],
                y = gear_data,
                mode = "lines",
                name = "Gear",
                line = dict(color = self.f1_colors['gear_color'], width = 2, shape = "hv"),
            ), row = row_idx, col = 1)

            fig.update_yaxes(
                title_text = "Gear",
                tickmode = "linear", dtick = 1, range = [0, 8.5],
                tickvals = [0, 1, 2, 3, 4, 5, 6, 7, 8],
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
                zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.5,
                row = row_idx, col = 1
            )

            fig.update_xaxes(
                title_text = "Distance (m)",
                tickmode = "linear", dtick = 1000, tickformat = ",",
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = False,
                zeroline = False,
                showticklabels = True,
                row = row_idx, col = 1
            )
            row_idx += 1


        # ==================================================
        # ---- LONGITUDINAL ACCEL ----
        # ==================================================
        
        if "longitudinal_accel_g" in telemetry.columns:
            fig.add_trace(go.Scatter(
                x = telemetry["Distance"],
                y = telemetry["longitudinal_accel_g"],
                mode = "lines",
                name = "Longitudinal Accel",
                line = dict(color = self.f1_colors['long_color'], width = 2),
            ), row = row_idx, col = 1)

            fig.update_yaxes(
                title_text = "g",
                range = [-6, 7],
                tickvals = [-6, -4, -2, 2, 4, 6],   # skip 0
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
                zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.5,
                row = row_idx, col = 1
            )

            fig.update_xaxes(
                title_text = "Distance (m)",
                tickmode = "linear", dtick = 1000, tickformat = ",",
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = False,
                zeroline = False,
                showticklabels = True,
                row = row_idx, col = 1
            )
            row_idx += 1

        # ==================================================
        # ---- LATERAL ACCEL ----
        # ==================================================
        
        if "lateral_accel_g" in telemetry.columns:
            lat_data = telemetry["lateral_accel_g"].dropna()
            lat_max = max(abs(lat_data.min()), abs(lat_data.max())) * 1.05  # auto-scale 

            fig.add_trace(go.Scatter(
                x = telemetry["Distance"],
                y = telemetry["lateral_accel_g"],
                mode = "lines",
                name = "Lateral Accel",
                line = dict(color = self.f1_colors['lat_color'], width = 2),
            ), row = row_idx, col = 1)

            fig.update_yaxes(
                title_text = "g",
                range = [-lat_max, lat_max],
                tickvals = [-6, -4, -2, -1, 0, 1, 2, 4, 6],
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = True, gridcolor = "rgba(200,200,200,0.15)",
                zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)", zerolinewidth = 0.5,
                row = row_idx, col = 1
            )

            fig.update_xaxes(
                title_text = "Distance (m)",
                tickmode = "linear", dtick = 1000, tickformat = ",",
                title_font = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                tickfont = dict(size = 12, color = "rgba(200,200,200,0.6)", family = "Arial"),
                showgrid = False,
                zeroline = False,
                showticklabels = True,
                row = row_idx, col = 1
            )
            row_idx += 1


        # ==================================================
        # ---- GLOBAL LAYOUT ----
        # ==================================================
        fig.update_layout(
            template = "plotly_dark",
            height = 350 * len(subplot_titles),
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            showlegend = False,
            font = dict(color = "#dddddd")
        )

        return fig

    # ---------------- Sector comparison ----------------
    # def create_sector_comparison_chart(self, sector_data, driver_code):
        
    #     # Create a simple bar chart comparing times across the 3 sectors.
        
    #     if not sector_data:
    #         return None

    #     try:
    #         sectors = ['Sector 1', 'Sector 2', 'Sector 3']
    #         times = [
    #             sector_data.get('sector_1', 0),
    #             sector_data.get('sector_2', 0),
    #             sector_data.get('sector_3', 0)
    #         ]

    #         # Convert to seconds if needed
    #         times_in_seconds = []
    #         for t in times:
    #             if hasattr(t, 'total_seconds'):
    #                 times_in_seconds.append(t.total_seconds())
    #             else:
    #                 times_in_seconds.append(float(t) if t else 0)

    #         fig = go.Figure(data=[
    #             go.Bar(
    #                 x = sectors,
    #                 y = times_in_seconds,
    #                 marker_color = self.f1_colors['primary'],
    #                 text = [f"{t:.3f}s" for t in times_in_seconds],
    #                 textposition = 'auto',
    #             )
    #         ])

    #         fig.update_layout(
    #             title = dict(
    #                 text = f"Sector Times", 
    #                 x = 0.5, 
    #                 xanchor = "center",
    #                 font = dict(color = '#888888', size = 20)
    #             ),
    #             xaxis_title = "Sector",
    #             yaxis_title = "Time (s)",
    #             template = "plotly_dark",
    #             height = 400,
    #             font = dict(family = "Arial", size = 12),
    #             plot_bgcolor = 'rgba(0,0,0,0)',
    #             paper_bgcolor = 'rgba(0,0,0,0)',
    #             margin = dict(l = 50, r = 30, t = 70, b = 50)
    #         )
    #         return fig

    #     except Exception as e:
    #         print(f"Error creating sector comparison chart: {e}")
    #         return None
