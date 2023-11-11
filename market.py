import random
from agents import RandomTrader, Chartist


class Market:
    def __init__(self, agents=100) -> None:
        self.BTC_prices = [0]
        self.BTC = 0  # number of BTC laying around. For example BTC sitting in Binance ready to be bought. Traders don't exchange directly.
        self.agents = []
        init_btc_range = (1, 20)
        init_gbp_range = (200, 10_000)
        for _ in range(agents // 5):
            self.agents.append(
                RandomTrader(btc_range=init_btc_range, gbp_range=init_gbp_range)
            )
            self.agents.append(
                Chartist(type=1, btc_range=init_btc_range, gbp_range=init_gbp_range)
            )
            self.agents.append(
                Chartist(type=2, btc_range=init_btc_range, gbp_range=init_gbp_range)
            )
            self.agents.append(
                Chartist(type=3, btc_range=init_btc_range, gbp_range=init_gbp_range)
            )
            self.agents.append(
                Chartist(type=4, btc_range=init_btc_range, gbp_range=init_gbp_range)
            )

    def calculate_total_btc(self):
        total_btc = 0
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

    def simulate(self, days):
        for day in range(days):
            if day % 90 == 0:
                self.add_BTC()
