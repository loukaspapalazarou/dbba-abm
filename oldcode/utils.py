import pandas as pd
import random


def load_btc_prices(filename, col):
    data = pd.read_csv(filename)
    return data[col].tolist()


def calculate_ema(n, close_prices):
    ema_values = [close_prices[0]]

    # Calculate EMA for the remaining data points
    for i in range(1, len(close_prices)):
        ema = (2 / (n + 1)) * close_prices[i] + (1 - 2 / (n + 1)) * ema_values[i - 1]
        ema_values.append(ema)
    return ema_values[-1]


def random_amount(full_amount, rate_range):
    return full_amount * random.uniform(*rate_range)
