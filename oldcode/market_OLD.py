import random
import math
import utils
import numpy as np
from agents import RandomTrader, Chartist


class Market:
    def __init__(
        self,
        agents=100,
        btc_range=(100, 1000),
        gbp_range=(100_000, 10_000_000),
        verbose=False,
    ) -> None:
        initial_btc = random.uniform(*btc_range)
        initial_gbp = random.uniform(*gbp_range)
        self.verbose = verbose
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
            self.agents.append(RandomTrader(id=i, verbose=self.verbose))
            self.agents.append(Chartist(id=i + 1, type=1, verbose=self.verbose))
            self.agents.append(Chartist(id=i + 2, type=2, verbose=self.verbose))
            self.agents.append(Chartist(id=i + 3, type=3, verbose=self.verbose))
            self.agents.append(Chartist(id=i + 4, type=4, verbose=self.verbose))
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
        action, delta_N = action[0], action[1]
        if action == "open":
            sign = 1
        else:
            sign = -1
        alpha = math.sqrt(2) / 2
        price_change = math.floor(alpha * sign * math.sqrt(abs(delta_N)))
        self.stats["btc_price"] += price_change

    def print_market_stats(self):
        print("Available BTC:", round(self.stats["available_btc"], 2))
        print("Available GBP:", round(self.stats["available_gbp"], 2))
        print("Current BTC Price:", round(self.stats["btc_price"], 2))

    def simulate(self, days):
        for day in range(days):
            self.stats["day"] = day
            if self.verbose:
                print(f"Day {day}\n--------------")
                self.print_market_stats()
                print("\nSimulating...")
            else:
                print(f"Day {day}...", end="")
            if (day + 1) % 90 == 0:
                self.add_BTC()
            random.shuffle(self.agents)
            for agent in self.agents:
                self.update_price(agent.trade(self.stats))
            self.stats["btc_close_prices"].append(self.stats["btc_price"])
            if self.verbose:
                print()
                self.print_market_stats()
                print(f"--------------")
                print("\n\n")
            else:
                print("done")

    def collect_statistics(self):
        pass
