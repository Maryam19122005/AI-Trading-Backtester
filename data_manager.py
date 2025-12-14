import yfinance as yf
import pandas as pd

class DataManager:
    def _init_(self, symbol, start=2000, end=2024):
        self.symbol = symbol
        self.start = start
        self.end = end

    def fetch_data(self):
        data = yf.download(self.symbol, start=self.start, end=self.end)
        data.dropna(inplace=True)
        data["Return"] = data["Close"].pct_change()
        return data