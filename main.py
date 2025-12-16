from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from data_manager import DataManager
from strategy import AITradingStrategy
from backtester import Backtester

def main():
    # -------------------------------
    # 1. Project Parameters
    # -------------------------------
    TICKER = "TSLA"
    START_DATE = "2024-01-01"
    END_DATE = datetime.today().strftime('%Y-%m-%d')  # automatically today
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
    data_with_signals = strategy.generate_signals(data, skip_last_day_signal=False)

    if data_with_signals is None:
        return

    # -------------------------------
    # 4. TODAY'S SIGNAL (with manual confirmation)
    # -------------------------------
    # Create 'User_Confirmed_Signal' column
    if 'User_Confirmed_Signal' not in data_with_signals.columns:
        data_with_signals['User_Confirmed_Signal'] = data_with_signals['Signal']

    # Split historical and today
    historical_data = data_with_signals.iloc[:-1].copy()
    today_data = data_with_signals.iloc[-1:].copy() 

    # Now overwrite **only the last day** based on user input
   # -------------------------------
    # 4. TODAY'S SIGNAL (manual confirmation)
    # -------------------------------
    today_signal_value = today_data['Signal'].iloc[0]
    today_close_price = today_data['Close'].iloc[0]
    today_date = today_data.index[0].date()

    # Ask user and set today_confirmed_signal
    if today_signal_value == 1:  # BUY
        user_choice = input(f"{today_date}: AI suggests BUY at ${today_close_price:.2f}. Buy? (yes/no): ").strip().lower()
        today_confirmed_signal = 1 if user_choice == "yes" else 0
    elif today_signal_value == -1:  # SELL
        user_choice = input(f"{today_date}: AI suggests SELL at ${today_close_price:.2f}. Sell? (yes/no): ").strip().lower()
        today_confirmed_signal = -1 if user_choice == "yes" else 0
    else:  # HOLD
        today_confirmed_signal = 0

    # Update both data_with_signals and today_data immediately
    data_with_signals.loc[data_with_signals.index[-1], 'User_Confirmed_Signal'] = today_confirmed_signal
    today_data['User_Confirmed_Signal'] = today_confirmed_signal


    # -------------------------------
    # 5. Backtesting
    # -------------------------------
    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    # Backtest only historical data
    portfolio_hist = backtester.run_backtest(historical_data)

    # Today’s confirmed trade
    today_signal = today_data['User_Confirmed_Signal'].iloc[0]
    today_price = today_data['Close'].iloc[0]

    if today_signal == 1:  # BUY today
        buy_shares = int(backtester.capital / today_price)
        backtester.shares += buy_shares
        backtester.capital -= buy_shares * today_price
        print(f"{today_date}: BUY {buy_shares} shares at ${today_price:.2f} (today confirmed)")

    elif today_signal == -1:  # SELL today
        backtester.capital += backtester.shares * today_price
        backtester.shares = 0
        print(f"{today_date}: SELL all shares at ${today_price:.2f} (today confirmed)")

    elif today_signal == 0:  # HOLD / skip today
        # Keep shares and capital exactly as they were at end of historical backtest
        backtester.capital = backtester.capital  # unchanged
        backtester.shares = backtester.shares    # unchanged
        print(f"{today_date}: No trade executed today. HOLD.")

    # Portfolio value for today
    today_total = backtester.capital + backtester.shares * today_price
    backtester.portfolio_value.append(today_total)



    # Add today row to portfolio dataframe
    today_data = today_data.copy()
    today_data['Holdings_Value'] = backtester.shares * today_price
    today_data['Total_Portfolio'] = today_total

    # Combine historical + today
    portfolio_data = pd.concat([portfolio_hist, today_data])
    final_metrics = backtester.calculate_metrics(portfolio_data)


    # -------------------------------
    # 6. Visualization (Matplotlib)
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
    buy_signals = data[data['User_Confirmed_Signal'] == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'],
                marker='^', label='BUY', alpha=0.8)

    # SELL signals
    sell_signals = data[data['User_Confirmed_Signal'] == -1]
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


if __name__ == "__main__":
    main()
