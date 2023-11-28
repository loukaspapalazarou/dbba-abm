from agent import RandomTrader, Chartist, LoucasAgent
from market_utils import *
import utils
import random
from parameters import *
import math
import os
from matplotlib import pyplot as plt
import pandas as pd
from tqdm import tqdm
import time


class Market:
    def __init__(
        self,
        num_agents=NUM_AGENTS,
        rule1n=CHARTIST_RULE_1_N,
        rule2n=CHARTIST_RULE_2_N,
        include_loucas=False,
    ) -> None:
        self.btc_close_prices = utils.load_historic_btc_prices(
            "BTC-GBP.csv",
            "Close",
            start_date="2018-11-25",
            end_date="2020-01-01",
        )
        self.btc_reserved = RESERVED_BTC
        self.btc_price = self.btc_close_prices[-1]
        self.initial_btc_price = self.btc_price
        self.current_day = 0
        self.rule1n = rule1n
        self.rule2n = rule2n
        self.last_simulation_time = -1
        self.agents = self.init_agents(num_agents, include_loucas)
        self.include_loucas = include_loucas
        self.cyberattack_day = None

        self.gbp = random.uniform(*MARKET_GBP_INIT)
        self.btc = MARKET_BTC_INIT
        self.total_btc = self.get_total_btc()

    def init_agents(self, num_agents, include_loucas):
        agents = []
        i = 0
        agent_range = (
            range(num_agents // 6) if include_loucas else range(num_agents // 5)
        )
        for _ in agent_range:
            agents.append(RandomTrader(id=i))
            agents.append(
                Chartist(id=i + 1, type=1, rule1n=self.rule1n, rule2n=self.rule2n)
            )
            agents.append(
                Chartist(id=i + 2, type=2, rule1n=self.rule1n, rule2n=self.rule2n)
            )
            agents.append(
                Chartist(id=i + 3, type=3, rule1n=self.rule1n, rule2n=self.rule2n)
            )
            agents.append(
                Chartist(id=i + 4, type=4, rule1n=self.rule1n, rule2n=self.rule2n)
            )
            i += 5
            if include_loucas:
                agents.append(LoucasAgent(id=i + 5))
                i += 1

        return agents

    def get_market_stats(self):
        return MarketStats(self.btc_price, self.btc_close_prices, self.current_day)

    def get_total_btc(self):
        return self.btc + sum(a.btc for a in self.agents)

    def get_total_gbp(self):
        return self.gbp + sum(a.gbp for a in self.agents)

    def release_new_btc(self):
        new_btc = self.btc_reserved * 0.6
        self.btc_reserved -= new_btc
        # 30% of traders will get the new bitcoin
        random_group = random.choices(self.agents, k=int(len(self.agents) * 0.3))
        random_group_total_btc = sum(a.btc for a in random_group)
        proportions = [a.btc / random_group_total_btc for a in random_group]
        for agent, proportion in zip(random_group, proportions):
            agent.btc += new_btc * proportion

    def execute_order(self, agent, order):
        if order is None:
            return
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

        proportion = order.btc / (self.total_btc - self.btc) * 100

        price_shift = math.floor(math.sqrt(2) / 2 * sign * proportion)
        self.btc_price += price_shift
        self.btc_price = max(self.btc_price, 0.001)

    def cyberattack(self):
        random.shuffle(self.agents)
        for i in range(int(len(self.agents) * 0.4)):
            order = Order(OrderType.CLOSE, self.agents[i].btc)
            self.execute_order(self.agents[i], order)
            self.agents[i].blocked = True

    def simulate(self, days=NUM_DAYS, cyberattack=False, dir=EXPERIMENT_NAME):
        start = time.perf_counter()
        for day in tqdm(range(days), desc=f"Simulating {dir}"):
            self.current_day = day
            if day % 90 == 0:
                self.release_new_btc()
            self.total_btc = self.get_total_btc()
            if cyberattack and day > int(days * 0.8):
                self.cyberattack()
                cyberattack = False
                self.cyberattack_day = day
            random.shuffle(self.agents)
            for agent in self.agents:
                if agent.blocked:
                    continue
                order = agent.trade(self.get_market_stats())
                self.execute_order(agent, order)
                self.update_price(order)
            self.btc_close_prices.append(self.btc_price)
        self.last_simulation_time = time.perf_counter() - start
        self.save_simulation_stats(dir)

    def save_simulation_stats(self, dir):
        stats = SimulationStats(include_loucas=self.include_loucas)
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
            stats.num_opened_positions[agent_type] += agent.opened_positions
        for btc_key, gbp_key in zip(stats.btc_ratio, stats.gbp_ratio):
            stats.btc_ratio[btc_key] = stats.btc_ratio[btc_key] / total_btc
            stats.gbp_ratio[gbp_key] = stats.gbp_ratio[gbp_key] / total_gbp

        if not os.path.exists(dir):
            os.makedirs(dir)

        historical_prices = utils.load_historic_btc_prices(
            "BTC-GBP.csv", "Close", start_date="2018-11-25", end_date="2023-10-31"
        )
        plt.plot(self.btc_close_prices, label="Simulated Prices")
        plt.plot(historical_prices, label="Hisotrical Prices")
        plt.axvline(
            x=len(self.btc_close_prices) - NUM_DAYS, color="g", label="Simulation Start"
        )
        if self.cyberattack_day:
            plt.axvline(x=self.cyberattack_day, color="r", label="Cyberattack")
        plt.legend()
        plt.title("Bitcoin Close Prices")
        plt.xlabel("Day (Historical + Simulated)")
        plt.ylabel("Price(GBP)")
        plt.savefig(dir + "/btc_close_prices.pdf")
        plt.clf()

        values = [self.btc]
        labels = ["Liquidity Pool"]
        for k in stats.btc_ratio:
            values.append(stats.btc_ratio[k])
            labels.append(k)
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Bitcoin Ratio")
        plt.tight_layout()
        plt.savefig(dir + "/btc_ratio.pdf")
        plt.clf()

        values = [self.gbp]
        labels = ["Liquidity Pool"]
        for k in stats.gbp_ratio:
            values.append(stats.gbp_ratio[k])
            labels.append(k)
        plt.pie(values, labels=labels, autopct="%1.1f%%")
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
        plt.ylabel("GBP + Current BTC Value")
        plt.tight_layout()
        plt.savefig(dir + "/wealth_acquisition.pdf")
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
        plt.title("Opened Positions")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(dir + "/opened_positions.pdf")
        plt.clf()

        data = {
            "Agent Type": list(stats.btc_ratio.keys()),
            "BTC Ratio": list(stats.btc_ratio.values()),
            "GBP Ratio": list(stats.gbp_ratio.values()),
            "Wealth Acquisition": list(stats.wealth_acquisition.values()),
            "Opened Positions": list(stats.num_opened_positions.values()),
        }
        df = pd.DataFrame(data)
        df = df.round(4)
        df.to_csv(os.path.join(dir, "simulation_stats.csv"), index=False)

        with open(f"{dir}/parameters.txt", "w") as f:
            f.write(f"NUM_DAYS={self.current_day+1}\n")
            f.write(f"NUM_AGENTS={len(self.agents)}\n")
            f.write(
                f"RANDOM_TRADER_TRADE_PROBABILITY={RANDOM_TRADER_TRADE_PROBABILITY}\n"
            )
            f.write(f"RULE 1 N={self.rule1n}\n")
            f.write(f"RULE 2 N={self.rule2n}\n")
            f.write(f"SIMULATION TIME={round(self.last_simulation_time,4)}s\n")
