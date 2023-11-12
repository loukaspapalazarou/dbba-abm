import random
import math
import utils
from agents import RandomTrader, Chartist


class Market:
    def __init__(
        self, agents=100, btc_range=(10, 10_000), gbp_range=(5_000, 100_000)
    ) -> None:
        initial_btc = btc_range[0] + (random.random() * btc_range[1])
        initial_gbp = gbp_range[0] + (random.random() * gbp_range[1])
        # initialize btc price with some real values
        historical_btc_close_prices = utils.load_btc_prices("BTC-GBP.csv", "Close")
        self.stats = {
            "day": 0,
            "btc_prices": historical_btc_close_prices,
            "btc_close_prices": historical_btc_close_prices,
            "available_btc": initial_btc,  # number of BTC laying around. For example BTC sitting in Binance ready to be bought. Traders don't exchange directly.
            "available_gbp": initial_gbp,
        }
        self.agents = []
        i = 0
        for _ in range(agents // 5):
            self.agents.append(RandomTrader(id=i))
            self.agents.append(Chartist(id=i + 1, type=1))
            self.agents.append(Chartist(id=i + 2, type=2))
            self.agents.append(Chartist(id=i + 3, type=3))
            self.agents.append(Chartist(id=i + 4, type=4))
            i += 5

    def calculate_total_btc(self):
        total_btc = self.stats["available_btc"]
        for a in self.agents:
            total_btc += a.BTC
        return total_btc

    def add_BTC(self):
        new_btc = self.calculate_total_btc() * 0.6
        # 30-70% of agents will get the additional bitcoin
        selected_agents = random.sample(
            self.agents,
            random.randint(int(len(self.agents) * 0.3), int(len(self.agents) * 0.7)),
        )
        total_btc_of_selected = sum(a.BTC for a in selected_agents)
        for agent in selected_agents:
            agent.BTC += new_btc * (agent.BTC / total_btc_of_selected)

    def update_btc_price(self):
        delta_N = self.stats["btc_prices"][-1] - self.stats["btc_prices"][-2]
        alpha = math.sqrt(2) / 2
        new_price = math.floor(alpha * math.sin(delta_N) * math.sqrt(abs(delta_N)))
        self.stats["btc_price"] = new_price

    def simulate(self, days):
        for day in range(days):
            if day % 90 == 0:
                self.add_BTC()
            for agent in self.agents:
                agent.trade(self.stats)
                self.update_btc_price()
            self.stats["btc_close_prices"].append(self.stats["btc_prices"][-1])
            self.stats["day"] = day
