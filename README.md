# Formula 1 Qualifying Lap Analysis

A comprehensive telemetry analysis tool for Formula 1 qualifying sessions, built with Streamlit and FastF1. Analyse pole position laps, compare drivers side-by-side, and visualise detailed telemetry data from 2018 onwards.

<br>

<img width="1888" height="769" alt="image" src="https://github.com/user-attachments/assets/2ea50737-7c5f-4aec-a437-f63e71a0dbe9" />

*Main application interface*

<br>

## Features

### 🏎️ Core Analysis Modes

- **Pole Position Analysis**: Automatically detect and analyse the pole-winning lap
- **Single Driver Analysis**: Select any driver from the qualifying session
- **Two-Driver Comparison**: Side-by-side telemetry and performance comparison

### 📊 Telemetry Visualisation

- **Speed Traces**: Lap-by-lap speed analysis with distance-based plotting
- **Throttle & Brake Inputs**: Detailed pedal application patterns
- **Gear Usage**: Gear selection throughout the lap
- **G-Forces**: Longitudinal and lateral acceleration analysis
- **Track Maps**: Speed-colored circuit visualisation showing faster sections

<br> 

<img width="1573" height="743" alt="image" src="https://github.com/user-attachments/assets/9871391f-48f8-4189-9067-a8d5893e79d7" />
<img width="1561" height="723" alt="image" src="https://github.com/user-attachments/assets/7e238bfe-cad7-4a17-8750-c32223e2abf4" />


*Speed, throttle, brake, and gear telemetry*

<br>

### ⏱️ Performance Metrics

- Maximum acceleration and braking forces (in g)
- Maximum and minimum speeds
- Cornering time percentage
- Full throttle percentage
- Heavy braking zones
- Sector time breakdowns
- Lap time comparisons

<img width="1532" height="566" alt="image" src="https://github.com/user-attachments/assets/79dc1476-d7ee-4493-a305-6137790da28b" />

*Key performance indicators*

<br>


### 🗺️ Track Visualisation

- **Speed-Colored Track Map**: Circuit layout colored by speed intensity
- **Comparison Track Map**: Shows which driver was faster at each track section
- **Delta Time Chart**: Visualises time gained/lost throughout the lap

<img width="1162" height="615" alt="image" src="https://github.com/user-attachments/assets/49ed142c-fa05-4206-9a00-a65ac71a3b5a" />

*Track map showing speed advantage by driver*

<br>

### 📈 Delta Analysis

Real-time delta chart showing where time is gained or lost between drivers across the entire lap distance.

<img width="1545" height="455" alt="image" src="https://github.com/user-attachments/assets/10f1db67-2496-46b4-8b63-2c0920f7853b" />

*Time delta analysis between two drivers*

<br>

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/f1-qualifying-analysis.git
cd f1-qualifying-analysis
```

2. Install required packages:
```bash
pip install -r requirement.txt
```

3. Run the application
```bash
python run_app.py
```

Or use Streamlit directly:
```bash
streamlit run main.py
```
The application will open in your default web browser at `http://localhost:8501`

## Usage

### Getting Started

1. **Select Year**: Choose a season from 2018 to the current year
2. **Select Grand Prix**: Pick from the available events for that season
3. **Load Session**: Click "LOAD SESSION" to fetch qualifying data
4. **Choose Analysis Mode**: 
   - Analyse Pole Position (automatic)
   - Analyse Specific Driver (manual selection)
   - Compare Two Drivers (side-by-side)

<br>

<img src="https://github.com/user-attachments/assets/4f86e8b9-9201-452d-ad71-15f28ba40047" height="700" alt="Sidebar 1">
<img src="https://github.com/user-attachments/assets/54579e6d-a79c-46f4-b48c-c48cc6458901" height="700" alt="Sidebar 2">
<img src="https://github.com/user-attachments/assets/4064959b-fd77-4f17-b8d3-f96d8b8d1da3" height="700" alt="Sidebar 3">

*Session selection interface*

<br>

### Analysis Modes

#### Single Driver Analysis
- Displays comprehensive telemetry for one driver
- Shows performance metrics and driving patterns
- Includes sector breakdown and track map

<br>
<img width="1572" height="663" alt="image" src="https://github.com/user-attachments/assets/d3c856ea-7a8f-44f5-8557-59333df5e28d" />
<img width="1579" height="639" alt="image" src="https://github.com/user-attachments/assets/617ae30d-4975-4985-9a0f-ecadb4767802" />
<img width="1552" height="706" alt="image" src="https://github.com/user-attachments/assets/10f3724a-45e3-41d1-bf25-de43ad6c9cb0" />
<img width="1543" height="695" alt="image" src="https://github.com/user-attachments/assets/71458a44-ff0c-43f6-9d05-aed0fdb87e3f" />
<img width="1608" height="736" alt="image" src="https://github.com/user-attachments/assets/e4520cba-4749-45a1-ba2d-938c075b09ff" />

*Single driver analysis view*

<br>

#### Two-Driver Comparison
- Side-by-side performance metrics
- Overlaid telemetry charts
- Delta time analysis
- Track map showing faster sections
- Sector time comparison

<br>

<img width="1542" height="678" alt="image" src="https://github.com/user-attachments/assets/6f43282d-9e49-4c98-8487-3dd92ffb407a" />
<img width="1540" height="621" alt="image" src="https://github.com/user-attachments/assets/58bda474-30b7-4a09-b7cf-7e6f45191171" />
<img width="1529" height="704" alt="image" src="https://github.com/user-attachments/assets/6d5ca271-6b54-4f79-81b4-11e91a97f016" />
<img width="1554" height="787" alt="image" src="https://github.com/user-attachments/assets/12f1be4e-6a0c-4b02-b3d0-3f3b8cda2b1e" />
<img width="1536" height="834" alt="image" src="https://github.com/user-attachments/assets/41d49ceb-df30-4eaf-acf4-57caea4a71f4" />


*Two-driver comparison view*

<br>

## Project Structure

```
f1-qualifying-analysis/
│
├── main.py                # Main application entry point
├── run_app.py             # Application launcher
├── requirement.txt        # Python dependencies
│
├── session_manager.py     # F1 session loading and driver management
├── data_analyser.py       # Telemetry analysis and metrics calculation
├── chart_creator.py       # Plotly chart generation
├── ui_styler.py           # Custom CSS styling
│
├── f1_cache/             # FastF1 data cache (auto-generated)

```

## Requirements

```
streamlit>=1.32.0
fastf1>=3.1.0
pandas>=2.2.0
numpy>=1.26.0
plotly>=5.20.0
scipy>=1.12.0
```

## Technical Details

### Data Source
- **FastF1**: Official F1 telemetry data API
- Coverage: 2018 season onwards
- Data includes: GPS coordinates, speed, throttle, brake, gear, sector times

### Calculations
- **Longitudinal Acceleration**: Calculated from speed differentials (m/s²)
- **Lateral Acceleration**: Derived from GPS coordinates and speed using curvature analysis
- **Distance**: Computed from GPS X/Y coordinates when not directly available
- **Smoothing**: Savitzky-Golay filter applied to reduce GPS noise

### Performance
- Session data is cached using `@st.cache_data` for faster reloads
- FastF1 cache stores downloaded data locally to minimise API calls
- Telemetry data is preprocessed once and reused for multiple visualisations

## Key Features Explained

### Track Map Colouring
The comparison track map uses colour coding to show which driver was faster at each section:
- **Red**: Driver 1 faster
- **Blue**: Driver 2 faster
- **Gray outline**: Reference track layout

### Delta Time Chart
Shows cumulative time difference throughout the lap:
- **Above zero**: Second driver is slower
- **Below zero**: Second driver is faster
- Final annotation shows the total lap time gap

### Driving Patterns
Quantifies driving style with three key metrics:
- **Cornering %**: Time spent below 200 km/h
- **Heavy Braking %**: Brake pressure above 50%
- **Full Throttle %**: Throttle at 98% or higher

## Troubleshooting

### Session Won't Load
- Check internet connection (FastF1 requires API access)
- Verify the selected year/GP combination exists
- Try clicking "RELOAD" to refresh the session

### Missing Telemetry Data
- Some sessions may have incomplete telemetry
- Try selecting a different driver or a recent season
- Pre-2018 data is not available

### Performance Issues
- Clear the `f1_cache` folder to reset cached data
- Restart the application
- Close other browser tabs using the same port

## Future Enhancements

- [ ] Race lap analysis support
- [ ] Practice session comparison
- [ ] Historical driver comparison across seasons
- [ ] Export analysis to PDF
- [ ] Custom track sector definitions
- [ ] Weather data integration
- [ ] Tire compound analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- **FastF1**: For providing the excellent F1 data API
- **Streamlit**: For the intuitive web app framework
- **Plotly**: For interactive data visualization
- **Formula 1**: For the amazing sport and data accessibility

## Contact

For questions, suggestions, or issues, please open an issue on GitHub.

---

**Note**: This application is for educational and analytical purposes only. All F1 data is accessed through the official FastF1 API and is subject to their terms of use.
```
