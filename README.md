# 🏁 Formula 1 Pole Position Qualifying Analysis App

An interactive **Streamlit application** that analyses Formula 1 **qualifying sessions (2018 to 2025)** using [FastF1](https://github.com/theOehrly/Fast-F1). It highlights **pole position laps**, visualises telemetry data, and provides insights into driver and team performance.

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

Run the app with:

```bash
streamlit run main.py
```

Then open the provided local URL in your browser. 

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

## ⚡ How It Works

1. Select a year (2018 onwards).
2. Choose a Grand Prix from that season.
3. Load the qualifying session.
4. Analyse the pole position lap:
   - View lap info, sector times, and tyre compound.
   - Explore telemetry (speed, throttle, brake, gear, acceleration).
   - Check performance metrics and visual track maps.

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

- Data is pulled directly from FastF1
- First load of a new session may take longer (data is cached locally).
- Supports sessions from 2018 to the latest completed season.

---

## 📜 License
This project is licensed under the MIT License. 



   
