from parameters import *
from market_utils import *
import random
from utils import calculate_ema


class Agent:
    def __init__(self, id) -> None:
        self.id = id
        self.btc = random.uniform(*AGENT_BTC_INIT)
        self.gbp = random.uniform(*AGENT_GBP_INIT)
        self.initial_btc = self.btc
        self.initial_gbp = self.gbp
        self.current_position = None
        self.opened_positions = 0
        self.blocked = False

    def whatami(self):
        s = type(self).__name__
        if s == "Chartist":
            s += "_" + str(self.type)
        return s

    def calculate_wealth_acquisition(self, current_btc_price, initial_btc_price):
        gbp_profit = self.gbp - self.initial_gbp
        btc_profit = (self.btc * current_btc_price) - (
            self.initial_btc * initial_btc_price
        )
        return gbp_profit + btc_profit


class RandomTrader(Agent):
    def trade(self, market_stats) -> Order:
        if random.random() < RANDOM_TRADER_TRADE_PROBABILITY:
            if self.current_position == None:
                order = Order(
                    OrderType.OPEN,
                    self.gbp / market_stats.btc_price,
                )
            else:
                order = Order(OrderType.CLOSE, self.btc)
            return order
        return None


class Chartist(Agent):
    def __init__(self, id, type, rule1n, rule2n) -> None:
        super().__init__(id)
        self.type = type
        self.rule1n = rule1n
        self.rule2n = rule2n

        match type:
            case 1:
                self.rule1open_weight = 0.8
                self.rule2open_weight = 0.2
                self.rule1close_weight = 0.8
                self.rule2close_weight = 0.2
            case 2:
                self.rule1open_weight = 0.8
                self.rule2open_weight = 0.2
                self.rule1close_weight = 0.2
                self.rule2close_weight = 0.8
            case 3:
                self.rule1open_weight = 0.2
                self.rule2open_weight = 0.8
                self.rule1close_weight = 0.8
                self.rule2close_weight = 0.2
            case 4:
                self.rule1open_weight = 0.2
                self.rule2open_weight = 0.8
                self.rule1close_weight = 0.2
                self.rule2close_weight = 0.8
            case _:
                raise ValueError("Chartist Type not Supported")

    def rule1open(self, market_stats):
        average_price_n_days = (
            sum(market_stats.btc_close_prices[: -self.rule1n]) / self.rule1n
        )
        if market_stats.btc_price < average_price_n_days:
            return True
        return False

    def rule1close(self, market_stats):
        if (
            market_stats.day - self.current_position.day <= self.rule1n
            and market_stats.btc_price > self.current_position.price
        ):
            return True
        return False

    def rule2open(self, market_stats):
        ema = calculate_ema(self.rule2n, market_stats.btc_close_prices)
        return market_stats.btc_price > ema

    def rule2close(self, market_stats):
        ema = calculate_ema(self.rule2n, market_stats.btc_close_prices)
        return self.current_position.price < ema

    def trade(self, market_stats) -> Order:
        if self.current_position is None:
            rule1_choice = self.rule1open(market_stats)
            rule2_choice = self.rule2open(market_stats)
            want_to_trade = random.choices(
                [rule1_choice, rule2_choice],
                weights=[self.rule1open_weight, self.rule2open_weight],
                k=1,
            )[0]
        else:
            rule1_choice = self.rule1close(market_stats)
            rule2_choice = self.rule2close(market_stats)
            want_to_trade = random.choices(
                [rule1_choice, rule2_choice],
                weights=[self.rule1close_weight, self.rule2close_weight],
                k=1,
            )[0]

        if not want_to_trade:
            return None

        if self.current_position == None and self.gbp > 0:
            order = Order(
                type=OrderType.OPEN,
                btc=self.gbp / market_stats.btc_price,
            )
        else:
            order = Order(type=OrderType.CLOSE, btc=self.btc)
        return order
