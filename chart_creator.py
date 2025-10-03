import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import sample_colorscale
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class ChartCreator:
    def __init__(self):
        
        # Standardised F1 color palette
        self.f1_colors = {
            'primary': '#ff1e30',
            'secondary': '#00ff00',
            'driver1_color': "#0000cd",  # Red for driver 1
            'driver2_color': "#ff1e30",  # Blue for driver 2
            'brake_color': '#ff0000',
            'background': '#0e1117'
        }

    # ---------------- Ensure distance column ----------------
    
    def _ensure_distance(self, telemetry):
        if "Distance" in telemetry.columns:
            return telemetry

        telemetry = telemetry.copy()
        if "X" in telemetry.columns and "Y" in telemetry.columns:
            dx = telemetry["X"].diff().fillna(0)
            dy = telemetry["Y"].diff().fillna(0)
            telemetry["Distance"] = np.cumsum(np.hypot(dx, dy))
        else:
            telemetry["Distance"] = np.arange(len(telemetry), dtype = float)

        return telemetry

    # ---------------- Comparison Track Map ----------------
    
    def create_comparison_track_map(self, telemetry1, telemetry2, driver1_code, driver2_code, rotate_deg = 235):
        # Create track map coloured by which driver was faster at each section
        if telemetry1 is None or telemetry1.empty or telemetry2 is None or telemetry2.empty:
            return None

        try:
            # ensure Distance exists
            telemetry1 = self._ensure_distance(telemetry1)
            telemetry2 = self._ensure_distance(telemetry2)

            # extract arrays
            x1 = telemetry1["X"].to_numpy(float)
            y1 = telemetry1["Y"].to_numpy(float)
            d1 = np.maximum.accumulate(telemetry1["Distance"].to_numpy(float))
            s1 = telemetry1["Speed"].to_numpy(float)

            x2 = telemetry2["X"].to_numpy(float)
            y2 = telemetry2["Y"].to_numpy(float)
            d2 = np.maximum.accumulate(telemetry2["Distance"].to_numpy(float))
            s2 = telemetry2["Speed"].to_numpy(float)

            # convert speed to km/h 
            if np.nanmedian(s1) < 60: 
                s1 *= 3.6
            if np.nanmedian(s2) < 60: 
                s2 *= 3.6

            # common distance grid over the overlap 
            lap_m = float(min(d1.max(), d2.max()))
            d = np.linspace(0.0, lap_m, 2000)

            # interpolate both speeds to common distance
            s1_i = np.interp(d, d1, s1)
            s2_i = np.interp(d, d2, s2)

            # --- smoothing to remove GPS jitter ---
            try:
                from scipy.signal import savgol_filter
                win = max(11, (len(d) // 150) * 2 + 1)  # odd window ~1–3% of lap
                s1_i = savgol_filter(s1_i, win, 2)
                s2_i = savgol_filter(s2_i, win, 2)
            except Exception:
                pass

            # speed difference at same distance (positive => driver1 faster)
            speed_diff = s1_i - s2_i

            # build reference path from driver1 coordinates resampled on the same grid
            x1_i = np.interp(d, d1, x1)
            y1_i = np.interp(d, d1, y1)

            # rotation
            ang = np.radians(rotate_deg)
            ca, sa = np.cos(ang), np.sin(ang)
            xr = ca * x1_i - sa * y1_i
            yr = sa * x1_i + ca * y1_i

            # masked segments for colouring without breaking path order
            # Positive differences (driver1 faster)
            x_pos = [x if dd >= 0 else None for x, dd in zip(xr, speed_diff)]
            y_pos = [y if dd >= 0 else None for y, dd in zip(yr, speed_diff)]
            cd_pos = [dd if dd >= 0 else None for dd in speed_diff]

            # Negative differences (driver2 faster)
            x_neg = [x if dd < 0 else None for x, dd in zip(xr, speed_diff)]
            y_neg = [y if dd < 0 else None for y, dd in zip(yr, speed_diff)]
            cd_neg = [abs(dd) if dd < 0 else None for dd in speed_diff]  # Use absolute values for display

            fig = go.Figure()

            # grey outline for full track reference
            fig.add_trace(go.Scatter(
                x = xr, y = yr, mode = "lines",
                line = dict(color = "lightgray", width = 3),
                showlegend = False, hoverinfo = "skip"
            ))

            # driver2 faster (blue segments)
            fig.add_trace(go.Scatter(
                x = x_neg, y = y_neg, mode = "lines",
                line = dict(color = "#0000CD", width = 2),
                name = driver2_code, showlegend = False,
                hovertemplate = f"{driver2_code} faster by: %{{customdata:.1f}} km/h<br>x: %{{x:.0f}}<br>y: %{{y:.0f}}<extra></extra>",
                customdata = cd_neg, connectgaps = False
            ))

            # driver1 faster (red segments)
            fig.add_trace(go.Scatter(
                x = x_pos, y = y_pos, mode = "lines",
                line = dict(color = "#DC143C", width = 2),
                name = driver1_code, showlegend = False,
                hovertemplate = f"{driver1_code} faster by: %{{customdata:.1f}} km/h<br>x: %{{x:.0f}}<br>y: %{{y:.0f}}<extra></extra>",
                customdata = cd_pos, connectgaps = False
            ))

            # legend markers (right hand side)
            fig.add_trace(go.Scatter(
                x = [None], y = [None], mode = "markers",
                marker = dict(color = "#DC143C", size = 16),
                name = f"{driver1_code}", hoverinfo = "skip", showlegend = True
            ))
            
            fig.add_trace(go.Scatter(
                x = [None], y = [None], mode = "markers",
                marker = dict(color = "#0000CD", size = 16),
                name = f"{driver2_code}", hoverinfo = "skip", showlegend = True
            ))

            # layout
            fig.update_xaxes(visible = False, constrain = "domain")
            fig.update_yaxes(visible = False, scaleanchor = "x", scaleratio = 1, constrain = "domain")
            fig.update_layout(
                height = 700, width = 900,
                margin = dict(l = 20, r = 120, t = 40, b = 20),
                legend = dict(
                    orientation = "h", yanchor = "middle", y = 0.75,
                    xanchor = "left", x = 1.01,
                    font = dict(size = 16, color = "#444444", family = "Arial")
                ),
                title = dict(
                    text = "Track Map: Speed Advantage by Driver",
                    font = dict(size = 20, color = "#888888"),
                    x = 0.5, 
                    xanchor = "center"
                ),
                plot_bgcolor="white"
            )
            return fig

        except Exception as e:
            print(f"Error creating comparison track map: {e}")
            return None

    # ---------------- Delta Chart ----------------
    
    def create_delta_chart(self, telemetry1, telemetry2, driver1_code, driver2_code):
        # Create time delta chart showing where driver2 gains/loses time vs driver1
        
            if telemetry1 is None or telemetry1.empty or telemetry2 is None or telemetry2.empty:
                return None

            def dist_time(df):
                # Return (distance_m, cumulative_time_s) with safe handling 
                d = df["Distance"].to_numpy(dtype=float)
                d = np.maximum.accumulate(d)  # enforce monotonic distance

                # true timestamps if present
                t_col = None
                for c in ("SessionTime", "Time", "LapTime", "Timestamp"):
                    if c in df.columns:
                        t_col = c
                        break

                if t_col is not None:
                    s = df[t_col]
                    if pd.api.types.is_timedelta64_dtype(s):
                        t = s.dt.total_seconds().to_numpy()
                    elif pd.api.types.is_datetime64_dtype(s):
                        t = (s - s.min()).dt.total_seconds().to_numpy()
                    else:
                        t = s.to_numpy(dtype=float)
                        # auto-convert ns -> s if values are too big
                        if t.size and np.median(np.abs(t[t != 0])) > 1e6:
                            t = t / 1e9
                    t0 = np.interp(d.min(), d, t)
                    return d, (t - t0)

                # integrate from speed (km/h -> m/s)
                v = df["Speed"].to_numpy(dtype = float)
                v = np.where(v > 60.0, v / 3.6, v)
                v = np.clip(v, 0.5, None)
                ds = np.diff(d, prepend = d[0])
                t = np.cumsum(ds / v)
                return d, (t - t[0])

            try:
                telemetry1 = self._ensure_distance(telemetry1)
                telemetry2 = self._ensure_distance(telemetry2)

                d1, t1 = dist_time(telemetry1)
                d2, t2 = dist_time(telemetry2)

                # common distance grid over the overlap
                lap_m = float(min(d1.max(), d2.max()))
                x = np.linspace(0.0, lap_m, 2000)
                t1i = np.interp(x, d1, t1)
                t2i = np.interp(x, d2, t2)

                # delta in seconds (driver2 - driver1)
                delta = t2i - t1i

                # savgol filter
                try:
                    from scipy.signal import savgol_filter
                    delta = savgol_filter(delta, 31, 2)
                except Exception:
                    pass

                final_gap = float(delta[-1])

                # ---- plot ----
                fig = go.Figure()
                fig.add_hline(y = 0, line_dash = "dash", line_color = "rgba(180,180,180,0.8)")
                fig.add_trace(go.Scatter(
                    x = x, y = delta, mode = "lines",
                    line = dict(width = 2, color = "#0000cd"),
                    name = f"Δ {driver2_code}-{driver1_code}",
                    hovertemplate = "Distance: %{x:.0f} m<br>Δ Time: %{y:.3f} s<extra></extra>"
                ))

                # note for user
                fig.add_annotation(
                    xref = "paper", yref = "paper",
                    x = 0, y = 1.12,
                    text = f"Notes: Above 0 = {driver2_code} slower | Below 0 = {driver2_code} faster<br>",
                    showarrow = False,
                    font = dict(size = 12, color = "gray", family = "Arial"),
                    align = "left"
                )
                
                # label the final gap at the right edge
                fig.add_annotation(
                    x = x[-1], y = delta[-1],
                    text = f"Final gap: {final_gap:+.3f}s",
                    showarrow = True, arrowhead = 2, ax = 40, ay = -20,
                    font=dict(size = 12, color = "#ff0000"),
                    bgcolor = "rgba(255,255,255,0.85)"
                )

                fig.update_layout(
                    template = "plotly_white",
                    xaxis = dict(
                        title = "Distance (m)",
                        title_font = dict(size = 14, color = "#444444", family = "Arial"),
                        tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                    ),
                    yaxis = dict(
                        title ="Δ Time (s)",
                        title_font = dict(size = 14, color = "#444444", family = "Arial"),
                        tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                    ),
                    showlegend = False,
                    height = 420,
                    margin = dict(l = 40, r = 20, t = 70, b = 40), 
                    font = dict(size = 12, color = "#444444", family = "Arial")
                )
                return fig

            except Exception as e:
                print(f"Error creating delta chart: {e}")
                return None

    # ---------------- Comparison Telemetry Chart ----------------
    
    def create_speed_comparison_chart(self, telemetry1, telemetry2, driver1_code, driver2_code):
        # Create speed comparison chart
        
        if telemetry1 is None or telemetry1.empty or telemetry2 is None or telemetry2.empty:
            return None

        telemetry1 = self._ensure_distance(telemetry1)
        telemetry2 = self._ensure_distance(telemetry2)

        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x = telemetry1["Distance"],
            y = telemetry1["Speed"],
            mode = "lines",
            name = driver1_code,
            line = dict(color = self.f1_colors['driver1_color'], width = 2)
        ))

        fig.add_trace(go.Scatter(
            x = telemetry2["Distance"],
            y = telemetry2["Speed"],
            mode = "lines",
            name = driver2_code,
            line = dict(color = self.f1_colors['driver2_color'], width = 2)
        ))

        fig.update_layout(
            title = dict(
                text = "Speed Comparison",
                font = dict(size = 20, color = '#888888'),
                x = 0.5,
                xanchor = 'center'
            ),
            template = "plotly_dark",
            height = 400,
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                title = "Distance (m)",
                tickmode = "linear",
                dtick = 1000,
                tickformat = ",",
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = False
            ),
            yaxis = dict(
                title = "km/h",
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = True,
                gridcolor = "rgba(200,200,200,0.15)"
            ),
            legend = dict(
                orientation = "h",
                yanchor = "bottom",
                y = 1.02,
                xanchor = "right",
                x = 1,
                font = dict(size = 14, color = '#444444')
            ),
            font = dict(color = "#444444")
        )
        
        return fig

    def create_throttle_comparison_chart(self, telemetry1, telemetry2, driver1_code, driver2_code):
        # Create throttle comparison chart
        
        if telemetry1 is None or telemetry1.empty or telemetry2 is None or telemetry2.empty:
            return None
        
        if "Throttle" not in telemetry1.columns or "Throttle" not in telemetry2.columns:
            return None

        telemetry1 = self._ensure_distance(telemetry1)
        telemetry2 = self._ensure_distance(telemetry2)

        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x = telemetry1["Distance"],
            y = telemetry1["Throttle"],
            mode = "lines",
            name = driver1_code,
            line = dict(color = self.f1_colors['driver1_color'], width = 2)
        ))

        fig.add_trace(go.Scatter(
            x = telemetry2["Distance"],
            y = telemetry2["Throttle"],
            mode = "lines",
            name = driver2_code,
            line = dict(color = self.f1_colors['driver2_color'], width = 2)
        ))

        fig.update_layout(
            title = dict(
                text = "Throttle Comparison",
                font = dict(size = 20, color = '#888888'),
                x = 0.5,
                xanchor = 'center'
            ),
            template = "plotly_dark",
            height = 400,
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                title = "Distance (m)",
                tickmode = "linear",
                dtick = 1000,
                tickformat = ",",
                title_font = dict(size = 12, color = "#444444", family = "Arial"), 
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = False
            ),
            yaxis = dict(
                title = "%",
                title_font = dict(size = 12, color = "#444444", family = "Arial"), 
                tickfont = dict(size = 12, color = "#444444", family = "Arial"), 
                showgrid = True,
                gridcolor = "rgba(200,200,200,0.60)"
            ),
            legend = dict(
                orientation = "h",
                yanchor = "bottom",
                y = 1.02,
                xanchor = "right",
                x = 1,
                font = dict(size = 14, color = '#444444')
            ),
            font = dict(color = "#444444")
        )
        
        return fig

    def create_brake_comparison_chart(self, telemetry1, telemetry2, driver1_code, driver2_code):
        # Create brake comparison chart
        
        if telemetry1 is None or telemetry1.empty or telemetry2 is None or telemetry2.empty:
            return None
        
        if "Brake" not in telemetry1.columns or "Brake" not in telemetry2.columns:
            return None

        telemetry1 = self._ensure_distance(telemetry1)
        telemetry2 = self._ensure_distance(telemetry2)

        brake1 = telemetry1["Brake"]
        brake2 = telemetry2["Brake"]
        
        if brake1.dtype == bool:
            brake1 = brake1.astype(int) * 100
        if brake2.dtype == bool:
            brake2 = brake2.astype(int) * 100

        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x = telemetry1["Distance"],
            y = brake1,
            mode = "lines",
            name = driver1_code,
            line = dict(color = self.f1_colors['driver1_color'], width = 2)
        ))

        fig.add_trace(go.Scatter(
            x = telemetry2["Distance"],
            y = brake2,
            mode = "lines",
            name = driver2_code,
            line = dict(color = self.f1_colors['driver2_color'], width = 2)
        ))

        fig.update_layout(
            title = dict(
                text = "Brake Comparison",
                font = dict(size = 20, color = '#888888'),
                x = 0.5,
                xanchor = 'center'
            ),
            template = "plotly_dark",
            height = 400,
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                title = "Distance (m)",
                tickmode = "linear",
                dtick = 1000,
                tickformat = ",",
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = False
            ),
            yaxis = dict(
                title = "%",
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = True,
                gridcolor = "rgba(200,200,200,0.60)"
            ),
            legend = dict(
                orientation = "h",
                yanchor = "bottom",
                y = 1.02,
                xanchor = "right",
                x = 1,
                font = dict(size = 14, color = '#444444')
            ),
            font = dict(color = "#444444")
        )
        
        return fig

    def create_driving_patterns_compare(self, metrics1, metrics2, driver1_code, driver2_code):
        
        # Two-driver horizontal driving-patterns chart 

        if not metrics1 or not metrics2:
            return None
        try:
            categories = ['Cornering', 'Heavy Braking', 'Full Throttle']
            colors     = ['#ffaa00', '#ff1e30', '#00ff41']  

            def vals(m):
                return [
                    int(m.get('cornering', 0) or 0),
                    int(m.get('heavy_braking', 0) or 0),
                    int(m.get('full_throttle', 0) or 0),
                ]

            v1 = vals(metrics1)
            v2 = vals(metrics2)
            xmax = max(max(v1), max(v2)) * 1.2 if (max(v1+v2) > 0) else 100

            fig = make_subplots(
                rows = 2, cols = 1, shared_xaxes = True,
                vertical_spacing = 0.12
            )

            # --- Driver 1 ---
            fig.add_trace(
                go.Bar(
                    x = v1, y = categories, orientation = "h",
                    marker_color = colors, width = 0.5,
                    hovertemplate = "%{y}: %{x}%<extra></extra>"
                ),
                row = 1, col = 1
            )

            # --- Driver 2 ---
            fig.add_trace(
                go.Bar(
                    x = v2, y = categories, orientation = "h",
                    marker_color = colors, width = 0.5,
                    hovertemplate="%{y}: %{x}%<extra></extra>"
                ),
                row = 2, col = 1
            )

            # --- Add % labels on the right of each bar ---
            for i, val in enumerate(v1):
                fig.add_annotation(
                    x = val + xmax*0.02, y = i, xref = "x1", yref = "y1",
                    text = f"{val}%", showarrow = False,
                    font = dict(size = 16, color="#44444"),
                    xanchor = "left", yanchor = "middle"
                )
            for i, val in enumerate(v2):
                fig.add_annotation(
                    x = val + xmax*0.02, y = i, xref = "x2", yref = "y2",
                    text = f"{val}%", showarrow = False,
                    font = dict(size = 16, color = "black"),
                    xanchor = "left", yanchor = "middle"
                )

            # --- Layout / axes ---
            fig.update_layout(
                height = 360,  
                margin = dict(l = 120, r = 80, t = 60, b = 30),
                plot_bgcolor = 'rgba(0,0,0,0)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                showlegend = False,
                bargap = 0.1,
                font = dict(color = "#888888", family = "Arial", size = 12)
            )

            fig.update_xaxes(
                range=[0, xmax],
                showgrid = False, showticklabels = False, showline = False, zeroline = False
            )
            
            fig.update_yaxes(
                showgrid = False, showline = False,
                tickfont = dict(size = 14, color = "#888888")
            )

            # lighter subtitle color
            for i in range(2):
                fig['layout']['annotations'][i]['font'] = dict(size = 16, color = "#666666")

            return fig

        except Exception as e:
            print(f"Error creating driving patterns comparison: {e}")
            return None
    
    # ---------------- Driving patterns ----------------
    
    def create_driving_patterns_chart(self, metrics, driver_code):
        
        if not metrics:
            return None

        try:
            categories = ['Cornering', 'Heavy Braking', 'Full Throttle']
            values = [
                int(metrics.get('cornering', 0) or 0),
                int(metrics.get('heavy_braking', 0) or 0),
                int(metrics.get('full_throttle', 0) or 0),
            ]
            colors = ['#ffaa00', '#ff1e30', '#00ff41']

            fig = go.Figure(go.Bar(
                x = values,
                y = categories,
                orientation = 'h',
                marker_color = colors,
                width = 0.5,
            ))

            for i, val in enumerate(values):
                fig.add_annotation(
                    x = val + 2,
                    y = i,
                    text = f"{val}%",
                    showarrow = False,
                    font = dict(size = 25, color = 'black'),
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
    
    def create_track_map_with_sectors(self, telemetry = None, driver_code = None, color_by_speed = True):
        if telemetry is None or telemetry.empty:
            return None

        try:
            telemetry = self._ensure_distance(telemetry)

            x = telemetry["X"].to_numpy(float)
            y = telemetry["Y"].to_numpy(float)

            fig = go.Figure()

            if not color_by_speed or "Speed" not in telemetry.columns:
                # simple continuous outline
                fig.add_trace(go.Scatter(
                    x = x, y = y, mode = "lines",
                    line = dict(color = "lightgray", width = 3),
                    hoverinfo = "skip", showlegend = False
                ))
            else:
                # gradient-by-speed: short line segments in Turbo colors
                import numpy as np
                from plotly.colors import sample_colorscale

                v = telemetry["Speed"].to_numpy(float)
                vmin, vmax = float(np.nanmin(v)), float(np.nanmax(v))
                span = max(vmax - vmin, 1e-9)

                max_segments = 1200
                step = max(1, int(np.ceil(len(x) / max_segments)))

                for i in range(0, len(x) - 1, step):
                    j = min(i + step, len(x) - 1)
                    vn = (np.nanmean(v[i:j]) - vmin) / span
                    color = sample_colorscale("Turbo", [vn])[0]
                    fig.add_trace(go.Scatter(
                        x = [x[i], x[j]], y = [y[i], y[j]],
                        mode="lines",
                        line = dict(color = color, width = 3),
                        hoverinfo = "skip", showlegend = False
                    ))

                # tiny invisible marker to display the colorbar
                fig.add_trace(go.Scatter(
                    x = [None], y = [None], mode = "markers",
                    marker = dict(
                        size = 0.01,
                        color = [vmin, vmax],
                        colorscale = "Turbo",
                        colorbar = dict(title = "Speed (km/h)", len = 0.8)
                    ),
                    hoverinfo = "skip", showlegend = False
                ))

            fig.update_layout(
                title = dict(text = "Track Map", x = 0.5, xanchor = "center",
                        font = dict(color = "#888888", size = 20)),
                template = "plotly_white",
                xaxis = dict(visible = False),
                yaxis = dict(visible = False, scaleanchor = "x", scaleratio = 1),
                height = 600,
                font = dict(family = "Arial", size = 12),
                plot_bgcolor = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)",
                margin = dict(l = 50, r = 30, t = 70, b = 50)
            )
            return fig

        except Exception as e:
            print(f"Error creting track map: {e}")
            return None        


    # ---------- Single-driver telemetry charts ----------

    def _base_line_fig(self, title_text: str, y_title: str, height: int = 400):
        # keep layouts consistent 
        fig = go.Figure()
        fig.update_layout(
            title = dict(text = title_text, font = dict(size = 20, color = '#888888'), x = 0.5, xanchor = 'center'),
            template = "plotly_white",
            height = height,
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                title = "Distance (m)",
                tickmode = "linear",
                dtick = 1000,
                tickformat = ",",
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = False,
            ),
            yaxis = dict(
                title = y_title,
                title_font = dict(size = 12, color = "#444444", family = "Arial"),
                tickfont = dict(size = 12, color = "#444444", family = "Arial"),
                showgrid = True,
                gridcolor = "rgba(200,200,200,0.60)",
            ),
            legend = dict(
                orientation = "h", yanchor = "bottom", y = 1.02,
                xanchor = "right", x = 1, font = dict(size = 14, color = "#444444")
            ),
            font = dict(color = "#444444"),
            showlegend = False
        )
        return fig

    def create_speed_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty:
            return None
        telemetry = self._ensure_distance(telemetry)

        fig = self._base_line_fig("Speed", "km/h")
        
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = telemetry["Speed"],
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('primary', '#ff1e30'), width = 2)
        ))
        
        fig.update_yaxes(
            tickvals = [0, 100, 200, 300, 400],
            zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)",
            rangemode = "tozero"
        )
        
        return fig

    def create_throttle_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty or "Throttle" not in telemetry.columns:
            return None
        telemetry = self._ensure_distance(telemetry)

        fig = self._base_line_fig("Throttle", "%")
        
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = telemetry["Throttle"],
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('secondary', '#f89fd3'), width = 2)
        ))
        
        fig.update_yaxes(tickvals = [20, 40, 60, 80, 100])
        
        return fig

    def create_brake_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty or "Brake" not in telemetry.columns:
            return None
        telemetry = self._ensure_distance(telemetry)

        brake = telemetry["Brake"]
        if brake.dtype == bool:  # convert boolean to percent
            brake = brake.astype(int) * 100

        fig = self._base_line_fig("Brake", "%")
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = brake,
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('brake_color', '#09f845'), width = 2)
        ))
        
        fig.update_yaxes(tickvals = [20, 40, 60, 80, 100])
        
        return fig

    def create_gear_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty:
            return None
        telemetry = self._ensure_distance(telemetry)

        gear_col = None
        for c in telemetry.columns:
            if c.lower() in ("gear", "ngear"):
                gear_col = c
                break
        if gear_col is None:
            return None

        gear_data = pd.to_numeric(telemetry[gear_col], errors = "coerce").fillna(0).astype(int)

        fig = self._base_line_fig("Gear", "Gear")
        
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = gear_data,
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('gear_color', '#800080'), width = 2, shape = "hv")
        ))
        
        fig.update_yaxes(tickmode = "linear", dtick = 1, range = [0, 8.5])

        return fig

    def create_longitudinal_accel_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty or "longitudinal_accel_g" not in telemetry.columns:
            return None
        telemetry = self._ensure_distance(telemetry)

        fig = self._base_line_fig("Longitudinal Acceleration", "g")
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = telemetry["longitudinal_accel_g"],
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('long_color', '#ffaa00'), width = 2)
        ))
        
        fig.update_yaxes(range = [-6, 7], tickvals = [-6, -4, -2, 0, 2, 4, 6],
                        zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)")
        
        return fig

    def create_lateral_accel_chart(self, telemetry, driver_code):
        if telemetry is None or telemetry.empty or "lateral_accel_g" not in telemetry.columns:
            return None
        telemetry = self._ensure_distance(telemetry)

        lat = telemetry["lateral_accel_g"].dropna()
        lat_max = (max(abs(lat.min()), abs(lat.max())) * 1.05) if len(lat) else 3.0

        fig = self._base_line_fig("Lateral Acceleration", "g")
        
        fig.add_trace(go.Scatter(
            x = telemetry["Distance"], y = telemetry["lateral_accel_g"],
            mode = "lines", name = driver_code,
            line = dict(color = self.f1_colors.get('lat_color', '#00aaff'), width = 2)
        ))
        
        fig.update_yaxes(range = [-lat_max, lat_max],
                        tickvals = [-6, -4, -2, -1, 0, 1, 2, 4, 6],
                        zeroline = True, zerolinecolor = "rgba(200,200,200,0.3)")
        return fig
