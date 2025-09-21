# 🏁 Formula 1 Pole Position Qualifying Analysis App

An interactive **Streamlit application** that analyses Formula 1 **qualifying sessions (2018 to 2025)** using [FastF1](https://github.com/theOehrly/Fast-F1). It highlights **pole position laps**, visualises telemetry data, and provides insights into driver and team performance.

---

## ⚠️ Important Note on Data Accuracy

This app leverages the official F1 API via the FastF1 library. It is crucial to understand the nature of this public data:

- ✅ Longitudinal Acceleration (Braking/Acceleration G-Forces) is Accurate: Calculated directly from high-quality velocity sensor data, these readings are reliable and show expected Formula 1 values (4-6G under braking, 2-3G under acceleration).
- ❌ Lateral Acceleration (Cornering G-Forces) is a Best-Effort Estimate: The API's X/Y positional data is intended for broadcast graphics, not high-precision GPS. Calculations of lateral acceleration (via v²/r) are derived from this low-resolution data and will show implausibly low values (~1G). This is a fundamental data constraint, not a bug in this app. The dashboard provides these values for trend analysis only.

‼️ __The app focuses on what the data can reliably tell us: longitudinal performance, driver inputs, and speed traces.__ ‼️

---

## ✨ Features

- 📅 **Historical Coverage**: Analyse qualifying sessions from 2018 to 2025.
- 🏎️ **Pole Position Focus**: Automatically detects and analyses the pole-winning lap.
- 📊 **Telemetry Analysis**: Speed, Throttle, Brake, Gear, Longitudinal and lateral acceleration
- 🗺️ **Track Visualisation**: Speed-coloured track maps.
- 📉 **Performance Metrics**: Max speed/min speed, Max acceleration & braking forces, Max lateral g-forces, Throttle and braking usage patterns
- 📂 **Dynamic Calendar**: Loads the correct Grand Prix events for each year.
- 👥 **Driver & Team Info**: Displays season-accurate line-ups.

---

## 🛠️ Tech Stack

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [FastF1](https://github.com/theOehrly/Fast-F1) 
- [Plotly](https://plotly.com/python/) 
- [NumPy](https://numpy.org/) / [Pandas](https://pandas.pydata.org/) 
- [SciPy](https://scipy.org/) 

---

## 📦 Installation

1. Clone the repository:
   
      ```bash
   git clone https://github.com/yourusername/f1-qualifying-analysis.git
   cd f1-qualifying-analysis
      ```
      
2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```
   
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. Run the app with:

```bash
streamlit run main.py
```

2. Wait for the app to launch. It will automatically open in your default browser, typically at http://localhost:8501.
3. In the sidebar:
     - Select a year (from 2018 to the present).
     - Select a Grand Prix from that season's calendar.
     - Click Load Session to fetch and cache the data. The first time for a new session may take a moment.
4. Explore! The main panel will populate with information about the pole position lap, interactive telemetry charts, and performance metrics.

---

## 📂 Project Structure

```bash
f1-qualifying-analysis/
│
├── main.py              # Streamlit entry point
├── session_manager.py   # Handles session loading & drivers
├── data_analyser.py     # Telemetry analysis & calculations
├── chart_creator.py     # Plotly chart generation
├── ui_styler.py         # CSS customisation for Streamlit UI
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🔍 How It Works

1. Session Loading: The app uses FastF1 to fetch session timing and telemetry data, storing it in a local cache for future speed.
2. Pole Identification: Finds the fastest lap and driver from the qualifying session results.
3. Data Processing: Telemetry data is cleaned and processed (e.g., acceleration is calculated from speed, signals are smoothed with a Savitzky-Golay filter).
4. Visualisation: Processed data is passed to Plotly to create interactive, hover-enabled charts within the Streamlit interface.

---

## 📸 Screenshots 

Welcome page:

<img width="1895" height="845" alt="image" src="https://github.com/user-attachments/assets/feeace4a-6670-4041-9463-a89b5c6d8cf0" />


After Track selection:

<img width="273" height="814" alt="image" src="https://github.com/user-attachments/assets/a284dbd9-47dc-49cc-9365-523f645e06ef" />


Pole Position Analysis: 

<img width="1508" height="718" alt="image" src="https://github.com/user-attachments/assets/4f2cf97a-014a-43c6-84bc-9318898f65fe" />
<img width="1522" height="638" alt="image" src="https://github.com/user-attachments/assets/a335ff24-e901-41b1-bc6c-d06a41498453" />
<img width="1555" height="593" alt="image" src="https://github.com/user-attachments/assets/edeaab61-e242-4b33-843e-181f0fb104ab" />
<img width="1535" height="630" alt="image" src="https://github.com/user-attachments/assets/01722ad7-2afe-4e08-b515-7f422bdc38ab" />
<img width="1513" height="584" alt="image" src="https://github.com/user-attachments/assets/3e99e5f9-febc-45de-8374-47cea6c59bea" />


---

## 📝 Notes

- The first time you load a new session, there will be a delay as data is downloaded from the FastF1 API and cached locally. Subsequent loads will be significantly faster.
- The accuracy of the data is dependent on the official F1 API. Some historical sessions may have incomplete telemetry.

---

## 🙏 Acknowledgments

- Thanks to the [FastF1](https://github.com/theOehrly/Fast-F1) library for providing a fantastic interface to the F1 data.
- Data sourced from the official Formula 1 API.

---

## 📜 License
This project is licensed under the MIT License. 



   
