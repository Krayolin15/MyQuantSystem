Markdown
# 📊 Advanced Quant Trading System & Dashboard

A professional-grade quantitative trading prototype featuring an event-driven backtesting engine and a real-time visual dashboard.

## 🚀 Overview
This project is designed to analyze market data, backtest trading strategies (starting with a Golden Cross SMA strategy), and visualize results in a professional web interface.

### Core Components:
* **`quant_system.py`**: The "Backend Engine." Uses `backtrader` for event-driven strategy simulation, commission handling, and trade logging.
* **`dashboard.py`**: The "Frontend UI." A modern Streamlit-based dashboard using `Plotly` for interactive candlestick charting and performance metrics.

---

## 🛠️ Installation & Setup

Before running the system, ensure you have Python installed. Install the required dependencies using pip:

```bash
pip install backtrader yfinance streamlit plotly pandas matplotlib

📈 How to Use
1. Run the Backtesting Engine
To test the strategy logic and see trade logs in the terminal:
python quant_system.py

2. Launch the Visual Dashboard
To open the interactive "Bloomberg-style" terminal in your browser:
streamlit run dashboard.py
