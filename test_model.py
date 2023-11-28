from parameters import *
from market import Market
import multiprocessing


def run_sim(n_vals, cyberattack=False):
    n1, n2 = n_vals
    m = Market(num_agents=NUM_AGENTS, rule1n=n1, rule2n=n2)
    name = f"n1_{str(n1)}-n2_{str(n2)}"
    if cyberattack:
        name += "-cyberattack"
    m.simulate(days=NUM_DAYS, cyberattack=cyberattack, dir=name)


if __name__ == "__main__":
    nums = [1, 7, 15, 30]
    n_vals = set()
    for i in nums:
        for j in nums:
            n_vals.add((i, j))

    procs = []
    for n in n_vals:
        p = multiprocessing.Process(
            target=run_sim,
            args=(n,),
        )
        procs.append(p)
        p.start()

    for t in procs:
        t.join()
