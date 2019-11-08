import sql

stocks_files = ["nasdaq_clean.txt", "nyse_clean.txt"]

stocks = []
bad_stocks = []
bad_stocks.extend(open("bad_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])
rare_stocks = []
rare_stocks.extend(open("rare_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])


for stocks_file in stocks_files:
  stocks.extend(open(stocks_file, "r", encoding="ascii").read().split("\n")[:-1])

stocks = [s.replace("\x00","") for s in stocks]
stocks = [s for s in stocks if s not in bad_stocks]

with sql.SQL() as c:
  for stock in stocks:
    rare = 1 if stock in rare_stocks else 0
    c.set("INSERT INTO stocks SET name=\"" + stock + "\"" + ",rare=" + str(rare))
