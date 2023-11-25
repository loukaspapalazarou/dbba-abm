from enum import Enum


class Position:
    def __init__(self, btc, day, price) -> None:
        self.btc = btc
        self.day = day
        self.price = price


class OrderType(Enum):
    OPEN = "open"
    CLOSE = "close"


class Order:
    def __init__(self, agent, type: OrderType, btc, day) -> None:
        self.agent = agent
        self.type = type
        self.btc = btc
        self.day = day


class MarketStats:
    def __init__(self, btc_price, btc_close_prices, day) -> None:
        self.btc_price = btc_price
        self.btc_close_prices = btc_close_prices
        self.day = day
