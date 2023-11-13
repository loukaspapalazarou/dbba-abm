import random
import math
import utils
import numpy as np
from agents import RandomTrader, Chartist


class Market:
    def __init__(
        self, agents=100, btc_range=(100, 1000), gbp_range=(100_000, 10_000_000)
    ) -> None:
        initial_btc = btc_range[0] + (random.random() * btc_range[1])
        initial_gbp = gbp_range[0] + (random.random() * gbp_range[1])
        # initialize btc price with some real values
        historical_btc_close_prices = utils.load_btc_prices("BTC-GBP.csv", "Close")
        self.stats = {
            "day": 0,
            "btc_price": historical_btc_close_prices[-1],
            "btc_close_prices": historical_btc_close_prices[:-1],
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
            random.randint(int(len(self.agents) * 0.4), int(len(self.agents) * 0.8)),
        )
        total_btc_of_selected = sum(a.BTC for a in selected_agents)
        for agent in selected_agents:
            agent.BTC += new_btc * (agent.BTC / total_btc_of_selected)

    def update_price(self, action):
        if action is None:
            return
        delta_N = random.uniform(-1000, 1000)
        alpha = math.sqrt(2) / 2
        price_change = math.floor(
            alpha * math.copysign(1, delta_N) * math.sqrt(abs(delta_N))
        )

        if action == "open":
            self.stats["btc_price"] += price_change
        elif action == "close":
            self.stats["btc_price"] -= price_change

        self.stats["btc_price"] = max(self.stats["btc_price"], 0)

    def print_market_stats(self):
        print("Available BTC:", round(self.stats["available_btc"], 2))
        print("Available GBP:", round(self.stats["available_gbp"], 2))
        print("Current BTC Price:", round(self.stats["btc_price"], 2))

    def simulate(self, days, verbose=False):
        for day in range(days):
            self.stats["day"] = day
            if verbose:
                print(f"Day {day}\n--------------")
                self.print_market_stats()
                print()
            else:
                print(f"Day {day}...", end="")
            if (day + 1) % 90 == 0:
                self.add_BTC()
            random.shuffle(self.agents)
            for agent in self.agents:
                action = agent.trade(self.stats)
                self.update_price(action)
            self.stats["btc_close_prices"].append(self.stats["btc_price"])
            if verbose:
                print()
                self.print_market_stats()
                print(f"--------------")
                print("\n\n")
            else:
                print("done")

    def collect_statistics(self):
        pass
