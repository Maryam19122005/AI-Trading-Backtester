from data_manager import DataManager

dm = DataManager("TSLA", "2022-01-01", "2024-01-01")
data = dm.fetch_data()

print(data.head())
