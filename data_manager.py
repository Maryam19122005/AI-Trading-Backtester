import yfinance as yf
import pandas as pd
import numpy as np

class DataManager:
    """
    Handles data acquisition, cleaning, and initial feature calculation.
    (Step 1 of the Project Workflow)
    """
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = None

    def fetch_data(self):
        """Retrieves historical OHLCV data using yfinance."""
        print(f"Fetching data for {self.ticker}...")
        try:
            # Fetch OHLCV data from the API
            self.data = yf.download(
                self.ticker, 
                start=self.start_date, 
                end=self.end_date, 
                progress=False
            )
            if self.data.empty:
                raise ValueError(f"No data returned for ticker {self.ticker}.")
            else:
                print(f"Data fetched successfully.")
                print(self.data)
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            self.data = None
        
        return self.data

    def preprocess_data(self):
        #Performs data cleaning and calculates initial features.
        if self.data is None:
            print("Data is not loaded. Please run fetch_data first.")
            return None

        # 1. Data Cleaning
        # Drop any rows with missing values (part of data cleaning)
        initial_rows = len(self.data)
        self.data.dropna(inplace=True)      #will remove the null values from data
        print(f"Cleaned data: Dropped {initial_rows - len(self.data)} rows with NaN values.")

        # 2. Calculate Initial Features (Daily Returns and Volatility)
        # Calculate daily returns (a core requirement for initial features)
        self.data['Daily_Return'] = self.data['Close'].pct_change()     #pandas function to calculate the percentage difference by a formula 
        # Calculate volatility (initial features for model input)
        # Using a 20-day rolling standard deviation of returns
        self.data['Volatility_20d'] = self.data['Daily_Return'].rolling(window=20).std()

        # Final dropna() after calculations to remove initial NaN values created by rolling window
        self.data.dropna(inplace=True)

        return self.data

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # Define your parameters for a common stock (e.g., Apple,tesla,microsoft)
    TICKER = 'TSLA'
    START_DATE = '2020-01-01'
    END_DATE = '2024-01-01' # Note: End date is exclusive in yfinance

    # Create an instance of the DataManager
    data_manager = DataManager(TICKER, START_DATE, END_DATE)

    # Execute the steps
    ohlcv_data = data_manager.fetch_data()
    if ohlcv_data is not None:
        processed_data = data_manager.preprocess_data()
        
        if processed_data is not None:
            print("\n--- Processed Data Head (First 5 Rows) ---")
            print(processed_data.head())
            print(f"\nTotal rows after preprocessing: {len(processed_data)}")
            
            # This 'processed_data' will be the input for your Trading Strategy Class (Step 2)

