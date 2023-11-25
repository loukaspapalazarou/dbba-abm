import pandas as pd
import numpy


def load_historic_btc_prices(
    filename, col, start_date="2019-12-01", end_date="2020-01-01"
):
    df = pd.read_csv(filename)
    df["Date"] = pd.to_datetime(df["Date"])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    return df[col].tolist()


def calculate_ema(n, close_prices):
    close_prices = close_prices[:n]
    ema_values = [close_prices[0]]
    for i in range(1, len(close_prices)):
        ema = (2 / (n + 1)) * close_prices[i] + (1 - 2 / (n + 1)) * ema_values[i - 1]
        ema_values.append(ema)
    return ema_values[-1]


def absolute_value(val, vals):
    a = numpy.round(val / 100.0 * vals.sum(), 0)
    return a
