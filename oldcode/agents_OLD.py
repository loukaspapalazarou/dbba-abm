import random
from utils import calculate_ema, random_amount


class Position:
    def __init__(self, type, day, btc_price, btc, gbp) -> None:
        self.type = type
        self.day = day
        self.btc_price = btc_price
        self.BTC = btc
        self.GBP = gbp


class Agent:
    def __init__(
        self, id, btc_range=(1, 5), gbp_range=(200, 10_000), verbose=False
    ) -> None:
        self.id = id
        self.BTC = random.uniform(*btc_range)
        self.GBP = random.uniform(*gbp_range)
        self.positions = []
        self.verbose = verbose

    # only open and close here can manipulate the market_stats object
    def open(self, market_stats):
        btc_price = market_stats["btc_price"]
        gbp_to_give = random_amount(self.GBP, (0.3, 0.7))
        btc_to_get = gbp_to_give / btc_price

        if btc_to_get > market_stats["available_btc"] or self.GBP <= 0:
            return None

        # update self
        self.BTC += btc_to_get
        self.GBP -= gbp_to_give
        self.positions.append(
            Position("open", market_stats["day"], btc_price, btc_to_get, gbp_to_give)
        )

        # update market
        market_stats["available_btc"] -= btc_to_get
        market_stats["available_gbp"] += gbp_to_give

        if self.verbose:
            print(
                f"Agent {self.id} opened a position. Bought {round(btc_to_get,2)} BTC at {round(btc_price,2)} for {round(gbp_to_give,2)} GBP."
            )

        return ("open", btc_to_get)

    def close(self, market_stats):
        btc_price = market_stats["btc_price"]
        btc_to_give = self.positions[-1].BTC
        gbp_to_get = btc_to_give * btc_price

        if gbp_to_get > market_stats["available_gbp"] or self.BTC <= 0:
            return None

        # update self
        self.BTC -= btc_to_give
        self.GBP += gbp_to_get
        self.positions.append(
            Position("close", market_stats["day"], btc_price, btc_to_give, gbp_to_get)
        )

        # update market
        market_stats["available_btc"] += btc_to_give
        market_stats["available_gbp"] -= gbp_to_get

        if self.verbose:
            print(
                f"Agent {self.id} closed a position. Sold {round(btc_to_give,2)} BTC at {round(btc_price,2)} for {round(gbp_to_get,2)} GPB."
            )

        return ("close", btc_to_give)


class RandomTrader(Agent):
    # random trades have a 5% chance of trading in a given day
    def trade(self, market_stats):
        if random.random() < 0.05:
            return None
        if len(self.positions) == 0 or self.positions[-1].type == "close":
            return self.open(market_stats)
        return self.close(market_stats)


class Chartist(Agent):
    def __init__(self, id, verbose, type=None) -> None:
        super().__init__(id=id, verbose=verbose)
        self.rule1_n = 15
        self.rule2_n = 15
        self.type = type
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
            case _:
                raise ValueError("Chartist Type not Supported")

    def rule1open(self, market_stats) -> bool:
        # Check the Bitcoin price today compared to the average price in the
        # past n days. If the price today is lower than average price in the past n days, open
        # a position.
        current_btc_price = market_stats["btc_price"]
        prices = market_stats["btc_close_prices"][-self.rule1_n :]
        average = sum(prices) / len(prices)
        # print(
        #     f"-> Agent {self.id} - Type {self.type} - Rule 1 open: Average {average} | Current Price {current_btc_price} | {current_btc_price < average}"
        # )
        if current_btc_price < average:
            return True
        return False

    def rule1close(self, market_stats) -> bool:
        # If you opened a position in the past n days and the price is higher today,
        # close that position.
        # if we have not opened any positions in the past n days, rule is nil, and we return True or False with 50-50 change.
        if abs(self.positions[-1].day - market_stats["day"]) > self.rule1_n:
            return random.choice([True, False])
        # at this point we know that we have an open position in the last n days
        current_btc_price = market_stats["btc_price"]
        # print(
        #     f"-> Agent {self.id} - Type {self.type} - Rule 1 close: Last open order {abs(self.positions[-1].day - market_stats['day'])} days ago | Current Price {current_btc_price} | {current_btc_price > self.positions[-1].btc_price}"
        # )
        if current_btc_price > self.positions[-1].btc_price:
            return True
        return False

    def rule2open(self, market_stats) -> bool:
        # If the close price is higher than EMA(n), then open a position
        close_btc_price = market_stats["btc_close_prices"][-1]
        ema = calculate_ema(self.rule2_n, market_stats["btc_close_prices"])
        # print(
        #     f"-> Agent {self.id} - Type {self.type} - Rule 2 open: EMA {ema} | Closing Price {close_btc_price} | {close_btc_price > ema}"
        # )
        if close_btc_price > ema:
            return True
        return False

    def rule2close(self, market_stats) -> bool:
        # If the close price is lower than EMA(n) for an open position, close it.
        ema = calculate_ema(self.rule2_n, market_stats["btc_close_prices"])
        # print(
        #     f"-> Agent {self.id} - Type {self.type} - Rule 2 close: EMA {ema} | Open position price {self.positions[-1].btc_price} | {self.positions[-1].btc_price < ema}"
        # )
        if self.positions[-1].btc_price < ema:
            return True
        return False

    def try_open(self, market_stats):
        action = random.choices(
            [self.rule1open(market_stats), self.rule2open(market_stats)],
            weights=[self.rule1open_importance, self.rule2open_importance],
        )[0]
        if action == False:
            return None
        return self.open(market_stats)

    def try_close(self, market_stats):
        action = random.choices(
            [self.rule1close(market_stats), self.rule2close(market_stats)],
            weights=[self.rule1close_importance, self.rule2close_importance],
        )[0]
        if action == False:
            return None
        return self.close(market_stats)

    def trade(self, market_stats):
        if len(self.positions) == 0 or self.positions[-1].type == "close":
            return self.try_open(market_stats)
        return self.try_close(market_stats)
