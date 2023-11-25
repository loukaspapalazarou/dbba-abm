from agent import RandomTrader, Chartist
from market_utils import *
import utils
import random
from parameters import *
import math
import os
from matplotlib import pyplot as plt
import pandas as pd
from tqdm import tqdm
import shutil


class Market:
    def __init__(self, agents) -> None:
        self.btc_close_prices = utils.load_historic_btc_prices("BTC-GBP.csv", "Close")
        self.btc_price = self.btc_close_prices[-1]
        self.initial_btc_price = self.btc_price
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
        return self.btc + sum(a.btc for a in self.agents)

    def get_total_gbp(self):
        return self.gbp + sum(a.gbp for a in self.agents)

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
                agent.opened_positions += 1
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
        self.btc_price = max(self.btc_price, 0.001)

    def cyberattack(self):
        print("Cyberattack!")

    def simulate(self, days, cyberattack=False):
        for day in tqdm(range(days), desc="Simulating Days"):
            self.current_day = day
            if day % 90 == 0:
                self.add_btc()
            if cyberattack and day > int(days * 0.8):
                self.cyberattack()
                cyberattack = False
            random.shuffle(self.agents)
            for agent in self.agents:
                order = agent.trade(self.get_market_stats())
                self.execute_order(order)
                self.update_price(order)
            self.btc_close_prices.append(self.btc_price)

    def save_simulation_stats(self, dir="experiment"):
        stats = SimulationStats()
        total_btc = 0
        total_gbp = 0
        for agent in self.agents:
            agent_type = agent.whatami()
            stats.num_opened_positions[agent_type] += agent.opened_positions
            stats.btc_ratio[agent_type] += agent.btc
            stats.gbp_ratio[agent_type] += agent.gbp
            total_btc += agent.btc
            total_gbp += agent.gbp
            stats.wealth_acquisition[agent_type] += agent.calculate_wealth_acquisition(
                current_btc_price=self.btc_price,
                initial_btc_price=self.initial_btc_price,
            )
        for btc_key, gbp_key in zip(stats.btc_ratio, stats.gbp_ratio):
            stats.btc_ratio[btc_key] = stats.btc_ratio[btc_key] / total_btc
            stats.gbp_ratio[gbp_key] = stats.gbp_ratio[gbp_key] / total_gbp

        if not os.path.exists(dir):
            os.makedirs(dir)

        plt.plot(self.btc_close_prices)
        plt.title("Bitcoin Close Prices")
        plt.xlabel("Day")
        plt.ylabel("Price(GBP)")
        plt.savefig(dir + "/btc_close_prices.pdf")
        plt.clf()

        values = []
        labels = []
        for k in stats.btc_ratio:
            values.append(stats.btc_ratio[k])
            labels.append(k)
        plt.pie(values, labels=labels)
        plt.title("Bitcoin Ratio")
        plt.tight_layout()
        plt.savefig(dir + "/btc_ratio.pdf")
        plt.clf()

        values = []
        labels = []
        for k in stats.gbp_ratio:
            values.append(stats.gbp_ratio[k])
            labels.append(k)
        plt.pie(values, labels=labels)
        plt.title("GBP Ratio")
        plt.tight_layout()
        plt.savefig(dir + "/gbp_ratio.pdf")
        plt.clf()

        values = []
        labels = []
        for k in stats.wealth_acquisition:
            values.append(stats.wealth_acquisition[k])
            labels.append(k)
        plt.bar(labels, values)
        for i, value in enumerate(values):
            plt.text(
                i, value + 0.1, str(utils.millify(value)), ha="center", va="bottom"
            )
        plt.title("Wealth Acquisition")
        plt.ylabel("Amount(GBP)")
        plt.tight_layout()
        plt.savefig(dir + "/wealth_acquisition.pdf")
        plt.clf()

        data = {
            "Agent Type": list(stats.btc_ratio.keys()),
            "BTC Ratio": list(stats.btc_ratio.values()),
            "GBP Ratio": list(stats.gbp_ratio.values()),
            "Wealth Acquisition": list(stats.wealth_acquisition.values()),
        }
        df = pd.DataFrame(data)
        df = df.round(4)
        df.to_csv(os.path.join(dir, "simulation_stats.csv"), index=False)
        shutil.copyfile("parameters.py", dir + "/parameters_snapshot.py")
