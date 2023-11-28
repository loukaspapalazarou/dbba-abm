from parameters import *
from market import Market


if __name__ == "__main__":
    m = Market(include_loucas=False)
    m.simulate(cyberattack=False)
