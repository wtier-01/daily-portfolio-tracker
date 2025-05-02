# config.py

from pathlib import Path

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Path to portfolio CSV (tickers + shares)
CSV_PATH = DATA_DIR / "transactions.csv"

# === Portfolio Settings ===
BENCHMARK_TICKER = "SPY"  # default benchmark
TRADING_DAYS = 252        # used for annualized metrics

# === Display Settings ===
CURRENCY = "USD"
DECIMALS = 2

# Example: Add to config.py
TICKER_OPTIONS = [
    'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NVDA', 'META', 'NFLX', 'JPM', 'BAC',
    'V', 'MA', 'DIS', 'INTC', 'PYPL', 'PEP', 'KO', 'CSCO', 'ORCL', 'T', 'PFE', 'MRK'
]
