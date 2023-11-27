from parameters import *
from market import Market


if __name__ == "__main__":
    m = Market(agents=1000)
    m.simulate(days=NUM_DAYS, cyberattack=False)
