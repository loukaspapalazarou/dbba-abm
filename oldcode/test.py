import math
import random


def update_price(curr_price, action, amount):
    print(action, amount)
    if action is None:
        return
    delta_N = amount
    if action == "close":
        delta_N *= -1
    alpha = math.sqrt(2) / 2
    price_change = math.floor(
        alpha * math.copysign(1, delta_N) * math.sqrt(abs(delta_N))
    )

    return curr_price + price_change


price = 100
for _ in range(100):
    price = update_price(
        price, random.choice(["open", "close"]), price * random.uniform(1, 100)
    )
    print(price)
