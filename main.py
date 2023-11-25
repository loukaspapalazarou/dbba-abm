from parameters import *
from market import Market
from matplotlib import pyplot as plt

if __name__ == "__main__":
    m = Market(agents=10_000)
    m.simulate(days=NUM_DAYS)

    plt.plot(m.btc_close_prices)
    plt.show()
