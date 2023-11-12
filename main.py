from datetime import date
from market import Market

if __name__ == "__main__":
    # between January 1, 2020 and October 31, 2023.
    start = date(2020, 1, 1)
    end = date(2023, 10, 31)
    days = (end - start).days

    m = Market(agents=10)
    print(m.stats["btc_price"])
    # m.simulate(days=10)

    # TODO
    # Rules
    # Price update
    # Open and close
    # Extract stats from simulation
