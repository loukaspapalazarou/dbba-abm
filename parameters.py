from datetime import date
import numpy as np

# Name
EXPERIMENT_NAME = "experiment"

# Days
START_DATE = date(2020, 1, 1)
END_DATE = date(2023, 10, 31)
NUM_DAYS = (END_DATE - START_DATE).days

# Simulation scaledown
SCALEDOWN_FACTOR = 1 / 25_000

# Real numbers
NUM_AGENTS = int(60_000_000 * SCALEDOWN_FACTOR)
TOTAL_BTC = 19_000_000 * SCALEDOWN_FACTOR

# Simulation start
INITIAL_AVAILABLE_BTC = TOTAL_BTC * 0.6
RESERVED_BTC = TOTAL_BTC - INITIAL_AVAILABLE_BTC

MARKET_BTC_INIT = INITIAL_AVAILABLE_BTC * 0.1
TRADERS_ALLOCATED_BTC = INITIAL_AVAILABLE_BTC - MARKET_BTC_INIT

AGENT_BTC_INIT = TRADERS_ALLOCATED_BTC / NUM_AGENTS

AGENT_BTC_INIT = (
    AGENT_BTC_INIT + (AGENT_BTC_INIT * -0.5),
    AGENT_BTC_INIT + (AGENT_BTC_INIT * 0.5),
)  # traders get -10% or +10% of btc allocated to each one


CRYPTO_INVESTOR_DAILY_SPEND = (
    np.array([1_000, 10_000]) / 365
)  # average crypto investor spends 1k-10k a year on crypto
AGENT_GBP_INIT = CRYPTO_INVESTOR_DAILY_SPEND * NUM_DAYS

# Liquidity
MARKET_GBP_INIT = (500_000, 1_000_000)

# Variables
RANDOM_TRADER_TRADE_PROBABILITY = (
    0.01  # Empirically 1% change at any given day for random trader to act.
)
CHARTIST_RULE_1_N = 10
CHARTIST_RULE_2_N = 10
