# 📊 Daily Portfolio Tracker

The Daily Portfolio Tracker is a Python-based financial dashboard that allows users to build, track, and analyze a stock portfolio in real-time. The tool fetches live data using Yahoo Finance, calculates daily portfolio performance, visualizes historical trends, and provides intelligent alerts through an interactive Streamlit web interface.

---

## 🚀 Features

- 🔄 **Live Portfolio Builder** — Add and edit stock positions directly from the UI
- 💹 **Real-Time Price Tracking** — Automatically fetches current market prices for each asset
- 📈 **30-Day Historical Value Chart** — Visualize your portfolio’s growth or decline over time
- 📉 **Daily % Change Chart** — Track short-term market volatility
- 🧠 **Insights Dashboard** — See key metrics like best/worst day, 7-day average, and volatility
- 📊 **Diversification Breakdown** — View allocation across holdings using a dynamic pie chart
- ⚠️ **Alert System**  
  - Portfolio drop > 5%
  - High volatility (7-day std dev > 4%)
  - SPY outperformance > 5%

---

## 🗂️ Project Structure

```bash
daily_portfolio_tracker/
│
├── main.py                   # Streamlit app launcher
├── config.py                 # Global settings, ticker list, formatting
│
├── /data/
│   ├── transactions.csv      # User input for stocks & shares
│   └── portfolio.db          # SQLite DB for daily value snapshots
│
├── /engine/
│   ├── data_fetcher.py       # Fetches prices from yfinance
│   ├── portfolio_calculator.py  # Value, weights, insights, SPY comparison
│
├── /db/
│   └── db_manager.py         # Handles SQLite logging
│
├── /visuals/
│   └── dashboard.py          # Main Streamlit interface with tabs
│
└── README.md                 # Project documentation
