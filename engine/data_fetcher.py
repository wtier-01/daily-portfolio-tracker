# engine/data_fetcher.py

import yfinance as yf
import pandas as pd

def fetch_prices(tickers):
    """
    Fetch latest adjusted close prices for a list of tickers using yfinance.
    
    Parameters:
        tickers (list): List of stock or ETF tickers (e.g., ['AAPL', 'MSFT'])

    Returns:
        pandas.Series: Latest prices indexed by ticker
    """
    if not tickers:
        return pd.Series(dtype=float)

    # Download the most recent day of price data
    data = yf.download(tickers, period="1d", auto_adjust=True, progress=False)

    # Handle case where single ticker returns a Series instead of DataFrame
    if isinstance(data, pd.DataFrame):
        close_prices = data['Close'].iloc[-1]  # Last available row
    else:
        close_prices = pd.Series({tickers[0]: data['Close']})

    # Return prices as Series: {ticker: price}
    return close_prices
