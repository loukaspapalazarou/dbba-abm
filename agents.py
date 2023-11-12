import random


class Agent:
    def __init__(self, btc_range=(1, 5), gbp_range=(200, 10_000)) -> None:
        self.BTC = btc_range[0] + (random.random() * btc_range[1])
        self.GBP = gbp_range[0] + (random.random() * gbp_range[1])
        self.current_position = None

    def open(self):
        pass

    def close(self):
        pass


class RandomTrader(Agent):
    def trade(self):
        if random.random() < 0.6:
            return
        if self.current_position:
            self.close()
        else:
            self.open()


class Chartist(Agent):
    def __init__(self, type=None) -> None:
        super().__init__()
        match type:
            case 1:
                self.rule1open_importance = 0.8
                self.rule2open_importance = 0.2
                self.rule1close_importance = 0.8
                self.rule2close_importance = 0.2
            case 2:
                self.rule1open_importance = 0.8
                self.rule2open_importance = 0.2
                self.rule1close_importance = 0.2
                self.rule2close_importance = 0.8
            case 3:
                self.rule1open_importance = 0.2
                self.rule2open_importance = 0.8
                self.rule1close_importance = 0.8
                self.rule2close_importance = 0.2
            case 4:
                self.rule1open_importance = 0.2
                self.rule2open_importance = 0.8
                self.rule1close_importance = 0.2
                self.rule2close_importance = 0.8

    def rule1open(self) -> bool:
        pass

    def rule1close(self) -> bool:
        pass

    def rule2open(self) -> bool:
        pass

    def rule2close(self) -> bool:
        pass

    def try_open(self):
        action = random.choices(
            [self.rule1open(), self.rule2open()],
            weights=[self.rule1open_importance, self.rule2open_importance],
        )[0]
        if not action:
            return
        self.open()

    def try_close(self):
        action = random.choices(
            [self.rule1close(), self.rule2close()],
            weights=[self.rule1close_importance, self.rule2close_importance],
        )[0]
        if not action:
            return
        self.close()

    def trade(self):
        if self.current_position:
            self.try_close()
        else:
            self.try_open()
