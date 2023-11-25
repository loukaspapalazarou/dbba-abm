from agent import RandomTrader, Chartist
from market_utils import *
import utils
import random
from parameters import *
import math


class Market:
    def __init__(self, agents) -> None:
        self.btc_close_prices = utils.load_btc_prices("BTC-GBP.csv", "Close")
        self.btc_price = self.btc_close_prices[-1]
        self.btc = random.uniform(*MARKET_BTC_INIT)
        self.gbp = random.uniform(*MARKET_GBP_INIT)
        self.current_day = 0

        self.agents = []
        i = 0
        for _ in range(agents // 5):
            self.agents.append(RandomTrader(id=i))
            self.agents.append(Chartist(id=i + 1, type=1))
            self.agents.append(Chartist(id=i + 2, type=2))
            self.agents.append(Chartist(id=i + 3, type=3))
            self.agents.append(Chartist(id=i + 4, type=4))
            i += 5

    def get_market_stats(self):
        return MarketStats(self.btc_price, self.btc_close_prices, self.current_day)

    def get_total_btc(self):
        return sum(a.btc for a in self.agents)

    def add_btc(self):
        new_btc = int(self.get_total_btc() * 0.6)
        while new_btc > 0:
            min_btc = min(a.btc for a in self.agents)
            max_btc = max(a.btc for a in self.agents)
            random.shuffle(self.agents)
            for agent in self.agents:
                normalized_btc = (agent.btc - min_btc) / (max_btc - min_btc)
                if normalized_btc > random.random():
                    btc_to_get = max(1, int(new_btc * 0.1))
                    agent.btc += btc_to_get
                    new_btc -= btc_to_get

    def execute_order(self, order):
        if order is None:
            return
        agent = order.agent
        market_stats = self.get_market_stats()
        if order.type == OrderType.OPEN:
            if (
                agent.gbp >= order.btc * market_stats.btc_price
                and self.btc >= order.btc
            ):
                agent.gbp -= order.btc * market_stats.btc_price
                agent.btc += order.btc
                self.gbp += order.btc * market_stats.btc_price
                self.btc -= order.btc
                agent.current_position = Position(
                    order.btc, day=self.current_day, price=self.btc_price
                )
        elif order.type == OrderType.CLOSE:
            if (
                self.gbp >= order.btc * market_stats.btc_price
                and agent.btc >= order.btc
            ):
                agent.gbp += order.btc * market_stats.btc_price
                agent.btc -= order.btc
                self.gbp -= order.btc * market_stats.btc_price
                self.btc += order.btc
            agent.current_position = None

    def update_price(self, order):
        if order is None:
            return
        if order.type == OrderType.OPEN:
            sign = 1
        else:
            sign = -1

        price_shift = math.floor(math.sqrt(2) / 2 * sign * math.sqrt(order.btc))

        self.btc_price += price_shift

    def simulate(self, days):
        for day in range(days):
            self.current_day = day
            print(f"Day {day}")
            if day % 90 == 0:
                self.add_btc()
            random.shuffle(self.agents)
            for agent in self.agents:
                # agents need info about the market to trade
                order = agent.trade(self.get_market_stats())
                self.execute_order(order)
                self.update_price(order)
            self.btc_close_prices.append(self.btc_price)
