from parameters import *
from market import Market


if __name__ == "__main__":
    m = Market(agents=NUM_AGENTS)
    m.simulate(days=NUM_DAYS, cyberattack=False)
    m.save_simulation_stats(dir=EXPERIMENT_NAME)
