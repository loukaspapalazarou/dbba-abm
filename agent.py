from parameters import *
from market_utils import *
import random
from utils import calculate_ema


class Agent:
    def __init__(self, id) -> None:
        self.id = id
        self.btc = random.uniform(*AGENT_BTC_INIT)
        self.gbp = random.uniform(*AGENT_GBP_INIT)
        self.current_position = None


class RandomTrader(Agent):
    def trade(self, market_stats) -> Order:
        if random.random() < RANDOM_TRADER_TRADE_PROBABILITY:
            if self.current_position == None:
                order = Order(
                    self,
                    OrderType.OPEN,
                    self.gbp / market_stats.btc_price,
                    market_stats.day,
                )
            else:
                order = Order(self, OrderType.CLOSE, self.btc, market_stats.day)
            return order
        return None


class Chartist(Agent):
    def __init__(self, id, type) -> None:
        super().__init__(id)
        self.type = type

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
            sum(market_stats.btc_close_prices[:-CHARTIST_RULE_1_N]) / CHARTIST_RULE_1_N
        )
        if market_stats.btc_price < average_price_n_days:
            return True
        return False

    def rule1close(self, market_stats):
        if (
            market_stats.day - self.current_position.day <= CHARTIST_RULE_1_N
            and market_stats.btc_price > self.current_position.price
        ):
            return True
        return False

    def rule2open(self, market_stats):
        ema = calculate_ema(CHARTIST_RULE_2_N, market_stats.btc_close_prices)
        return market_stats.btc_close_prices[-1] > ema

    def rule2close(self, market_stats):
        ema = calculate_ema(CHARTIST_RULE_2_N, market_stats.btc_close_prices)
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

        if self.current_position == None:
            order = Order(
                self,
                OrderType.OPEN,
                self.gbp / market_stats.btc_price,
                market_stats.day,
            )
        else:
            order = Order(self, OrderType.CLOSE, self.btc, market_stats.day)
        return order
