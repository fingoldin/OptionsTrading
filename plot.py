import matplotlib.pyplot as plt
import numpy as np
import math
import stocks
import time
import sys

option_name = "MNK" if len(sys.argv) < 2 else sys.argv[1]

options = list(stocks.get_options(option_name))
options.sort(key=lambda x: x["e_b"])
option = options[-1]
print(option)

t = 24 * 3600 * math.floor(int(time.time()) / (24 * 3600))

option_prices = [ ((r["timestamp"]-t) / 3600, r["last_price"]) for r in stocks.get_options(option_name) if r["strike"] == option["strike"] and r["expiration_date"] == option["expiration_date"]]

prices = [ ((r["timestamp"]-t) / 3600, r["price"]) for r in stocks.get_prices(option_name) ]

option_prices_x = np.array([ t[0] for t in option_prices ])
option_prices_y = np.array([ t[1] for t in option_prices ])

prices_x = np.array([ t[0] for t in prices ])
prices_y = np.array([ t[1] for t in prices ])

#option_prices_x = (option_prices_x - np.mean(option_prices_x)) / np.std(option_prices_x)
if np.std(option_prices_y) == 0:
  option_prices_y *= 0
else:
  option_prices_y = (option_prices_y - np.mean(option_prices_y)) / np.std(option_prices_y)

#prices_x = (prices_x - np.mean(prices_x)) / np.std(prices_x)
prices_y = (prices_y - np.mean(prices_y)) / np.std(prices_y)

plt.plot(prices_x,prices_y)
plt.plot(option_prices_x,option_prices_y)
plt.show()
