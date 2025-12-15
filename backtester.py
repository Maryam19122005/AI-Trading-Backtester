import pandas as pd
import numpy as np

class Backtester:
    """
    Simulates trades based on signals and tracks portfolio performance.
    (Step 4 of the Project Workflow)
    """
    def __init__(self, initial_capital=100000.0):
        # Initial setup
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.shares = 0
        self.trades = pd.DataFrame(columns=['Date', 'Signal', 'Price', 'Cash', 'Shares'])
        self.portfolio_value = [] # To store total value (Cash + Shares * Price)

    def run_backtest(self, data):
        """Iterates through the data and executes trades based on 'Signal' column."""
        print("\n--- Starting Backtest Simulation ---")
        
        # 1. Prepare Data for Tracking
        # Copy the processed data to avoid modifying the original DataFrame
        df = data.copy()
        df['Holdings_Value'] = 0.0
        df['Total_Portfolio'] = self.initial_capital
        
        # 2. Iterative Trading Loop
        for i, row in df.iterrows():
            current_date = i.date()
            signal = row['Signal']
            price = row['Close']
            
            # Calculate the current value of the holdings before any trade
            current_holdings_value = self.shares * price
            
            # --- Decision Logic ---
            if signal == 1: # BUY signal
                if self.capital > 0:
                    # Buy as many shares as possible with available capital (simple full investment)
                    buy_shares = int(self.capital / price) 
                    cost = buy_shares * price
                    
                    self.shares += buy_shares
                    self.capital -= cost
                    
                    # Record the trade
                    self.trades.loc[len(self.trades)] = [current_date, 'BUY', price, self.capital, self.shares]
                    print(f"{current_date}: BUY {buy_shares} shares @ ${price:.2f}. Remaining Cash: ${self.capital:.2f}")

            elif signal == -1: # SELL signal
                if self.shares > 0:
                    # Sell all held shares
                    sales_revenue = self.shares * price
                    
                    self.capital += sales_revenue
                    self.shares = 0 # Shares reset to 0
                    
                    # Record the trade
                    self.trades.loc[len(self.trades)] = [current_date, 'SELL', price, self.capital, self.shares]
                    print(f"{current_date}: SELL ALL shares @ ${price:.2f}. Total Cash: ${self.capital:.2f}")

            # 3. Update Portfolio Value for the day
            total_value = self.capital + (self.shares * price)
            df.loc[i, 'Holdings_Value'] = self.shares * price
            df.loc[i, 'Total_Portfolio'] = total_value
            self.portfolio_value.append(total_value)
            
        print("--- Backtest Simulation Complete ---")
        self.final_metrics = self.calculate_metrics(df)
        return df

    def calculate_metrics(self, portfolio_data):
        """Calculates and prints key performance indicators (KPIs)."""
        final_value = portfolio_data['Total_Portfolio'].iloc[-1]
        total_return = (final_value / self.initial_capital) - 1
        
        # Calculate max drawdown (risk measure)
        # 1. Find the cumulative peak value up to that point
        cumulative_peak = portfolio_data['Total_Portfolio'].cummax()
        # 2. Calculate the drop from the peak (Drawdown)
        drawdown = (portfolio_data['Total_Portfolio'] - cumulative_peak) / cumulative_peak
        max_drawdown = drawdown.min()

        # Calculate annualized returns and volatility for Sharpe Ratio (assuming trading days ≈ 252/year)
        daily_returns = portfolio_data['Total_Portfolio'].pct_change().dropna()
        annualized_return = daily_returns.mean() * 252
        annualized_volatility = daily_returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
        sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else np.nan

        metrics = {
            'Initial Capital': f"${self.initial_capital:,.2f}",
            'Final Portfolio Value': f"${final_value:,.2f}",
            'Total Return (%)': f"{total_return * 100:.2f}%",
            'Max Drawdown (%)': f"{max_drawdown * 100:.2f}%",
            'Annualized Return (%)': f"{annualized_return * 100:.2f}%",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}"
        }
        
        print("\n--- Performance Metrics ---")
        for key, value in metrics.items():
            print(f"{key}: {value}")
            
        return metrics