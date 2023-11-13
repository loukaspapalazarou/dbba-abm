from datetime import date
from market import Market
from matplotlib import pyplot as plt

if __name__ == "__main__":
    # between January 1, 2020 and October 31, 2023.
    start = date(2020, 1, 1)
    end = date(2023, 10, 31)
    days = (end - start).days

    m = Market(agents=10)
    m.simulate(days=100)
    m.collect_statistics()

    pr = m.stats["btc_close_prices"]
    plt.plot(range(len(pr)), pr)
    plt.show()
