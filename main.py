from datetime import date
from market import Market

if __name__ == "__main__":
    # between January 1, 2020 and October 31, 2023.
    start = date(2020, 1, 1)
    end = date(2023, 10, 31)
    delta = end - start
    m = Market(agents=10)
    m.simulate(days=delta.days)
    print(delta.days)
