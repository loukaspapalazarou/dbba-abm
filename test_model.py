from parameters import *
from market import Market
import multiprocessing
from itertools import permutations


def run_sim(n_vals, cyberattack=False):
    n1, n2 = n_vals
    m = Market(agents=NUM_AGENTS, rule1n=n1, rule2n=n2)
    name = f"n1_{str(n1)}-n2_{str(n2)}"
    if cyberattack:
        name += "-cyberattack"
    m.simulate(days=NUM_DAYS, cyberattack=cyberattack, dir=name)


if __name__ == "__main__":
    n_vals = [1, 5, 10, 20, 50]
    n_vals = list(permutations(n_vals, 2))

    procs = []
    for n in n_vals:
        p = multiprocessing.Process(
            target=run_sim,
            args=(
                n,
                False,
            ),
        )
        procs.append(p)
        p.start()
        p = multiprocessing.Process(
            target=run_sim,
            args=(
                n,
                True,
            ),
        )
        procs.append(p)
        p.start()
    for t in procs:
        t.join()
