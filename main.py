from parameters import *
from market import Market


if __name__ == "__main__":
    m = Market(agents=NUM_AGENTS)
    m.simulate(days=NUM_DAYS, cyberattack=False)
    for a in m.agents:
        print(
            a.whatami(),
            a.calculate_wealth_acquisition(m.btc_price, m.initial_btc_price),
        )
    m.save_simulation_stats(dir=EXPERIMENT_NAME)
