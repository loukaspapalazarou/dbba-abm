import pandas as pd


def load_btc_prices(filename, col):
    data = pd.read_csv(filename)
    return data[col].tolist()


def calculate_ema(close_prices, n):
    ema_values = []

    # Calculate the initial SMA (Simple Moving Average)
    sma = sum(close_prices[:n]) / n
    ema_values.append(sma)

    # Calculate EMA for the remaining data points
    for i in range(n, len(close_prices)):
        ema = (2 / (n + 1)) * close_prices[i] + (1 - 2 / (n + 1)) * ema_values[-1]
        ema_values.append(ema)

    return ema_values[-1]
