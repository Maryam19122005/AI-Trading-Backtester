import matplotlib.pyplot as plt


from data_manager import DataManager
from strategy import AITradingStrategy
from backtester import Backtester


def main():
    # -------------------------------
    # 1. Project Parameters
    # -------------------------------
    TICKER = "TSLA"
    START_DATE = "2020-01-01"
    END_DATE = "2024-01-01"
    INITIAL_CAPITAL = 100000

    # -------------------------------
    # 2. Data Manager
    # -------------------------------
    data_manager = DataManager(TICKER, START_DATE, END_DATE)
    data = data_manager.fetch_data()

    if data is None:
        return

    data = data_manager.preprocess_data()
    if data is None:
        return

    # -------------------------------
    # 3. Trading Strategy (Linear Regression)
    # -------------------------------
    strategy = AITradingStrategy()
    data_with_signals = strategy.generate_signals(data)

    if data_with_signals is None:
        return

    # -------------------------------
    # 4. Backtesting
    # -------------------------------
    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    portfolio_data = backtester.run_backtest(data_with_signals)

    # -------------------------------
    # 5. Visualization (Matplotlib)
    # -------------------------------
    plot_price_and_signals(data_with_signals, TICKER)
    plot_equity_curve(portfolio_data)


# -------------------------------------------------
# Visualization Functions
# -------------------------------------------------
def plot_price_and_signals(data, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Close Price')

    # BUY signals
    buy_signals = data[data['Signal'] == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'],
                marker='^', label='BUY', alpha=0.8)

    # SELL signals
    sell_signals = data[data['Signal'] == -1]
    plt.scatter(sell_signals.index, sell_signals['Close'],
                marker='v', label='SELL', alpha=0.8)

    plt.title(f"{ticker} Price with Trading Signals")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_equity_curve(portfolio_data):
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_data.index,
             portfolio_data['Total_Portfolio'],
             label='Portfolio Value')

    plt.title("Portfolio Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.show()


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    main()

