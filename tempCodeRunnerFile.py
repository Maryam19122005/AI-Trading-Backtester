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
    # 4. TODAY'S SIGNAL (with manual confirmation)
    # -------------------------------
    # Create the column if it does not exist
    if 'User_Confirmed_Signal' not in data_with_signals.columns:
        data_with_signals['User_Confirmed_Signal'] = 0  # default 0 (HOLD)

    today_signal_value = data_with_signals['Signal'].iloc[-1]
    today_close_price = data_with_signals['Close'].iloc[-1]
    today_date = data_with_signals.index[-1].date()

    if today_signal_value == 1:
        print(f"{today_date}: AI Strategy suggests BUY today at price ${today_close_price:.2f}")
        user_choice = input("Do you want to BUY today? (yes/no): ").strip().lower()
        if user_choice == "yes":
            data_with_signals.loc[data_with_signals.index[-1], 'User_Confirmed_Signal'] = 1
            print(f"Confirmed BUY of stock at ${today_close_price:.2f}")
        else:
            print("Trade skipped by user.")

    elif today_signal_value == -1:
        print(f"{today_date}: AI Strategy suggests SELL today at price ${today_close_price:.2f}")
        user_choice = input("Do you want to SELL today? (yes/no): ").strip().lower()
        if user_choice == "yes":
            data_with_signals.loc[data_with_signals.index[-1], 'User_Confirmed_Signal'] = -1
            print(f"Confirmed SELL of stock at ${today_close_price:.2f}")
        else:
            print("Trade skipped by user.")

    else:
        print(f"{today_date}: AI Strategy suggests HOLD today at price ${today_close_price:.2f}")
        # HOLD = 0 automatically

    # -------------------------------
    # 5. Backtesting
    # -------------------------------
    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    # Make sure Backtester reads 'User_Confirmed_Signal' instead of 'Signal'
    portfolio_data = backtester.run_backtest(data_with_signals)


    # -------------------------------
    # 6. Visualization (Matplotlib)
    # -------------------------------
    plot_price_and_signals(data_with_signals, TICKER)
    plot_equity_curve(portfolio_data)
