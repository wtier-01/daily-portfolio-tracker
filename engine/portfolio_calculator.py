# engine/portfolio_calculator.py

import pandas as pd
import yfinance as yf
from config import CSV_PATH
from engine.data_fetcher import fetch_prices

def load_portfolio():
    return pd.read_csv(CSV_PATH)

def calculate_portfolio_value(portfolio_df):
    tickers = portfolio_df['ticker'].tolist()
    prices = fetch_prices(tickers)

    portfolio_df['price'] = portfolio_df['ticker'].map(prices)
    portfolio_df['value'] = portfolio_df['shares'] * portfolio_df['price']
    total_value = portfolio_df['value'].sum()

    if total_value == 0:
        portfolio_df['weight'] = 0
    else:
        portfolio_df['weight'] = portfolio_df['value'] / total_value

    return portfolio_df, total_value

def get_historical_portfolio_value(days=30):
    portfolio_df = load_portfolio()
    tickers = portfolio_df['ticker'].tolist()
    shares = portfolio_df.set_index('ticker')['shares'].to_dict()

    data = yf.download(tickers, period=f"{days}d", auto_adjust=True, progress=False)['Close']

    if isinstance(data, pd.Series):
        data = data.to_frame()

    for ticker in data.columns:
        if ticker in shares:
            data[ticker] = data[ticker] * shares[ticker]

    portfolio_value_series = data.sum(axis=1).reset_index()
    portfolio_value_series.columns = ['date', 'value']

    return portfolio_value_series

def get_daily_pct_change(days=30):
    df = get_historical_portfolio_value(days)
    df['daily_return'] = df['value'].pct_change() * 100  # % return
    return df[['date', 'daily_return']]

def get_spy_comparison(days=30):
    spy = yf.download("SPY", period=f"{days}d", auto_adjust=True, progress=False)['Close']
    portfolio = get_historical_portfolio_value(days)
    merged = portfolio.copy()
    merged['spy'] = spy.loc[merged['date']].values
    merged['portfolio_pct'] = merged['value'].pct_change().fillna(0).cumsum()
    merged['spy_pct'] = merged['spy'].pct_change().fillna(0).cumsum()
    return merged

def get_portfolio_insights():
    df = get_historical_portfolio_value(30)
    df['daily_return'] = df['value'].pct_change()

    return {
        "7-Day Moving Avg": df['value'].rolling(7).mean().iloc[-1],
        "Best Day": df['daily_return'].max() * 100,
        "Worst Day": df['daily_return'].min() * 100,
        "Volatility (std dev)": df['daily_return'].std() * 100
    }
