from enum import Enum


class SimulationStats:
    def __init__(self) -> None:
        temp = {
            "RandomTrader": 0,
            "Chartist_1": 0,
            "Chartist_2": 0,
            "Chartist_3": 0,
            "Chartist_4": 0,
        }
        self.gbp_ratio = temp.copy()
        self.btc_ratio = temp.copy()
        self.wealth_acquisition = temp.copy()
        self.num_opened_positions = temp.copy()


class Position:
    def __init__(self, btc, day, price) -> None:
        self.btc = btc
        self.day = day
        self.price = price


class OrderType(Enum):
    OPEN = "open"
    CLOSE = "close"


class Order:
    def __init__(self, type: OrderType, btc) -> None:
        # self.agent = agent
        self.type = type
        self.btc = btc
        # self.day = day


class MarketStats:
    def __init__(self, btc_price, btc_close_prices, day) -> None:
        self.btc_price = btc_price
        self.btc_close_prices = btc_close_prices
        self.day = day
