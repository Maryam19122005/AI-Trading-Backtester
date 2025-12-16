from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


class AITradingStrategy:

    def __init__(self):
        self.model = LinearRegression()

    def generate_signals(self, data, skip_last_day_signal=True):
        try:
            # -------------------------------
            # 1. Feature Creation
            # -------------------------------
            data['Prev_Close'] = data['Close'].shift(1)
            data.dropna(inplace=True)

            X = data[['Prev_Close']]   # Input feature
            y = data['Close']          # Target output

            # -------------------------------
            # 2. Train-Test Split
            # -------------------------------

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )

            # -------------------------------
            # 3. Model Training
            # -------------------------------
            self.model.fit(X_train, y_train)
            print("Model trained successfully using Linear Regression.")

            # -------------------------------
            # 4. Prediction (Full Data)
            # -------------------------------
            data['Predicted_Close'] = self.model.predict(X)

            # -------------------------------
            # 5. Signal Generation
            # -------------------------------
            data['Signal'] = 0
            data.loc[data['Predicted_Close'] > data['Close'], 'Signal'] = 1   # BUY
            data.loc[data['Predicted_Close'] < data['Close'], 'Signal'] = -1  # SELL

            # -------------------------------
            # 6. Skip last day signal if needed
            # -------------------------------
            if skip_last_day_signal:
                data.iloc[-1, data.columns.get_loc('Signal')] = 0

            print("AI trading signals generated.")
            return data

        except Exception as e:
            print("AI Strategy Error:", e)
            return None

