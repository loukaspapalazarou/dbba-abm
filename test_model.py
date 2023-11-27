from parameters import *
from market import Market
import multiprocessing


def run_sim(n_vals):
    name, n1, n2 = n_vals
    m = Market(agents=NUM_AGENTS, rule1n=n1, rule2n=n2)
    m.simulate(days=NUM_DAYS, cyberattack=False, dir=name)


if __name__ == "__main__":
    n_vals = [("5-5", 5, 5), ("10-10", 10, 10), ("5-10", 5, 10), ("10-5", 10, 5)]
    procs = []
    for n in n_vals:
        p = multiprocessing.Process(target=run_sim, args=(n,))
        procs.append(p)
        p.start()

        # complete the processes
    for t in procs:
        t.join()
