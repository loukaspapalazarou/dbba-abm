import random
from matplotlib import pyplot as plt


def calculate_ema(n, close_prices):
    close_prices = close_prices[-n:]
    ema_values = [close_prices[0]]
    for i in range(1, len(close_prices)):
        ema = (2 / (n + 1)) * close_prices[i] + (1 - 2 / (n + 1)) * ema_values[i - 1]
        ema_values.append(ema)
    return ema_values


n = 5

vals = [random.randint(0, 100_000) for _ in range(100)]
ema_vals = calculate_ema(n, vals)
avg = [sum(vals) / len(vals)]

while len(avg) < len(vals):
    avg.insert(0, 0)
while len(ema_vals) < len(vals):
    ema_vals.insert(0, 0)

plt.plot(vals)
plt.plot(ema_vals)
plt.plot(avg, "ro")

plt.show()
