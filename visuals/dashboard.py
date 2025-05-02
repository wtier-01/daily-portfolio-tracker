# visuals/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from engine.portfolio_calculator import (
    load_portfolio,
    calculate_portfolio_value,
    get_historical_portfolio_value,
    get_daily_pct_change,
    get_spy_comparison,
    get_portfolio_insights
)
from db.db_manager import (
    init_db,
    insert_snapshot,
    get_latest_snapshots
)
from config import CURRENCY, DECIMALS, TICKER_OPTIONS, CSV_PATH

# ===== ALERT SETTINGS =====
DAILY_DROP_ALERT_THRESHOLD = -5.0      # % drop triggers daily alert
VOLATILITY_ALERT_THRESHOLD = 4.0        # % std dev triggers volatility alert
SPY_UNDERPERFORMANCE_THRESHOLD = 5.0    # % lag triggers SPY underperformance alert
# ===========================

def run():
    st.set_page_config(page_title="Daily Portfolio Tracker", layout="wide")
    st.title("📊 Daily Portfolio Tracker")

    st.sidebar.header("🛠️ Build Your Portfolio")

    selected_tickers = st.sidebar.multiselect(
        "Choose stocks to track:",
        options=TICKER_OPTIONS,
        default=["AAPL", "MSFT"]
    )

    share_inputs = {}
    if selected_tickers:
        st.sidebar.subheader("Enter shares per stock")
        for ticker in selected_tickers:
            shares = st.sidebar.number_input(f"{ticker} shares", min_value=1, max_value=1000, value=10)
            share_inputs[ticker] = shares

        if st.sidebar.button("💾 Save Portfolio"):
            df = pd.DataFrame(list(share_inputs.items()), columns=["ticker", "shares"])
            df.to_csv(CSV_PATH, index=False)
            st.sidebar.success("Portfolio saved!")

    try:
        init_db()
        portfolio_df = load_portfolio()
        portfolio_df, total_value = calculate_portfolio_value(portfolio_df)
        insert_snapshot(total_value)

        snapshots = get_latest_snapshots(n=2)
        daily_change = None

        if len(snapshots) == 2:
            _, prev_value = snapshots[0]
            _, curr_value = snapshots[1]
            daily_change = ((curr_value - prev_value) / prev_value) * 100

        tab1, tab2, tab3 = st.tabs(["📊 Tracker", "📈 SPY Comparison", "📋 Insights"])

        # === TRACKER TAB ===
        with tab1:
            # ===== ALERTS =====
            if daily_change is not None and daily_change <= DAILY_DROP_ALERT_THRESHOLD:
                st.error(f"⚠️ Alert: Your portfolio dropped {daily_change:.2f}% today!")

            try:
                pct_df = get_daily_pct_change(days=30)
                volatility = pct_df['daily_return'].std()
                if volatility * 100 > VOLATILITY_ALERT_THRESHOLD:
                    st.warning(f"⚡ Alert: Portfolio volatility is high at {volatility * 100:.2f}%!")

            except Exception as e:
                st.warning(f"Could not calculate volatility for alert: {e}")

            try:
                comp_df = get_spy_comparison()
                final_portfolio = comp_df['portfolio_pct'].iloc[-1]
                final_spy = comp_df['spy_pct'].iloc[-1]
                underperformance = (final_spy - final_portfolio) * 100

                if underperformance >= SPY_UNDERPERFORMANCE_THRESHOLD:
                    st.error(f"⬇️ Alert: Portfolio underperformed SPY by {underperformance:.2f}% over 30 days.")

            except Exception as e:
                st.warning(f"Could not calculate SPY underperformance for alert: {e}")

            # ===== HEADER =====
            subheader_text = f"💰 Total Portfolio Value: {CURRENCY} ${total_value:,.{DECIMALS}f}"

            if daily_change is not None:
                change_symbol = "▲" if daily_change >= 0 else "▼"
                change_color = "green" if daily_change >= 0 else "red"
                subheader_text += f"  \n<span style='color:{change_color}'>{change_symbol} {daily_change:.2f}%</span>"

            st.subheader(subheader_text)
            st.markdown("---", unsafe_allow_html=True)

            # ===== PORTFOLIO TABLE =====
            formatted_df = portfolio_df.copy()
            formatted_df['price'] = formatted_df['price'].map(lambda x: f"${x:,.{DECIMALS}f}")
            formatted_df['value'] = formatted_df['value'].map(lambda x: f"${x:,.{DECIMALS}f}")
            formatted_df['weight'] = formatted_df['weight'].map(lambda x: f"{x:.1%}")
            st.dataframe(formatted_df[['ticker', 'shares', 'price', 'value', 'weight']])

            # ===== HISTORICAL VALUE CHART =====
            st.subheader("📈 Portfolio Value Over Time (Past 30 Days)")
            try:
                hist_df = get_historical_portfolio_value(days=30)
                fig = px.line(
                    hist_df, x='date', y='value',
                    title='Historical Portfolio Value',
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Total Value (USD)",
                    yaxis_tickprefix="$",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Unable to load historical portfolio data: {e}")

            # ===== DAILY PERCENT CHANGE CHART =====
            st.subheader("📉 Daily % Change (Past 30 Days)")
            try:
                fig = px.line(
                    pct_df, x='date', y='daily_return',
                    title="Daily % Change",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Daily Return (%)",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Unable to plot daily % change: {e}")

            # ===== DIVERSIFICATION BREAKDOWN =====
            st.subheader("📊 Diversification Breakdown")
            try:
                pie_chart = px.pie(
                    portfolio_df,
                    names='ticker',
                    values='weight',
                    title="Portfolio Allocation by Stock",
                    hole=0.4
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Unable to create diversification chart: {e}")

        # === SPY COMPARISON TAB ===
        with tab2:
            st.subheader("📈 Portfolio vs SPY (Last 30 Days)")
            try:
                comp_df = get_spy_comparison()
                fig = px.line(
                    comp_df, x='date', y=['portfolio_pct', 'spy_pct'],
                    labels={'value': 'Cumulative Return'},
                    title="Cumulative Return: Portfolio vs SPY"
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Cumulative Return",
                    template="plotly_white",
                    legend_title="Legend"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load SPY comparison: {e}")

        # === INSIGHTS TAB ===
        with tab3:
            st.subheader("📋 Portfolio Insights (Last 30 Days)")
            try:
                insights = get_portfolio_insights()
                for metric, value in insights.items():
                    if isinstance(value, float):
                        value = f"{value:,.2f}" if 'Avg' in metric else f"{value:.2f}%"
                    st.markdown(f"**{metric}:** {value}")
            except Exception as e:
                st.warning(f"Could not calculate portfolio insights: {e}")

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
