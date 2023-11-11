import random


class Agent:
    def __init__(self, BTC=None, GBP=None, btc_range=None, gbp_range=None) -> None:
        if BTC:
            self.BTC = BTC
        else:
            self.BTC = btc_range[0] + (random.random() * btc_range[1])
        if GBP:
            self.GBP = GBP
        else:
            self.GBP = gbp_range[0] + (random.random() * gbp_range[1])


class Chartist(Agent):
    def __init__(
        self, BTC=None, GBP=None, btc_range=None, gbp_range=None, type=None
    ) -> None:
        super().__init__(BTC, GBP, btc_range, gbp_range)
        match type:
            case 1:
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass


class RandomTrader(Agent):
    pass
