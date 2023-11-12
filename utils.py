import pandas as pd


def load_btc_prices(filename, col):
    data = pd.read_csv(filename)
    return data[col].tolist()
