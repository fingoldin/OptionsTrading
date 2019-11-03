Scraping data from stock and options data from Yahoo and Marketwatch and using them to build options trading algorithms.

First scrape_parallel.py scrapes the data and loads it into data_parallel.txt.
Then analyze.py sorts the data and then returns that to data.txt.

To do:

 - Scrape implied volatility and use it in calculations

 - Have another break calculation for what percentage stock price has to go down in order to lose 50% of expected profit. (This will favor in-the-money options.)

 - Add another json file which contains the sorted stocks so it can be used for further analyzation.
