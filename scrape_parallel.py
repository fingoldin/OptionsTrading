import urllib
from bs4 import BeautifulSoup
import sys
import ssl
import json
import time
from multiprocessing import Pool

start_time = time.time()

stocks_files = ["nasdaq_clean.txt", "nyse_clean.txt"]
priority_stock_files = ["priority_ebid_stocks.txt"]
price_max = 7.00
volume_min = 10

stocks = []
nonpriority = []
for stocks_file in priority_stock_files:
    stocks.extend(open(stocks_file, "r", encoding="ascii").read().split("\n")[:-1])
if (not input("Hit enter for full scrape")):
    for stocks_file in stocks_files:
        lst = open(stocks_file, "r", encoding="ascii").read().split("\n")
        nonpriority.extend([s for s in lst if s not in stocks and s not in nonpriority])
nonpriority.sort()
stocks.extend(nonpriority)

bad_stocks = []
rare_stocks = []
bad_stocks.extend(open("bad_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])
rare_stocks.extend(open("rare_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])

fp = open("data_parallel.txt", "w")
fp.write("")
fp.close()

stocks = [s.replace("\x00","") for s in stocks]
stocks = [s for s in stocks if s not in bad_stocks]

def clean(v):
  return v.replace("-","0").replace(",","")

def toi(v):
  return int(clean(v.string))

def tof(v):
  return float(clean(v.string))

def generateWeekOrder(weeks, totalWeeks):
    lst = []
    for i in weeks:
        if (i <= totalWeeks and i > 0):
            lst.append(i)
    for i in range(1,totalWeeks+1):
        if i not in lst:
            lst.append(i)
    return lst

def get_stock(stock):
  if (stock in bad_stocks):
      print(stock + " is a bad stock \n")
      return
  nweeks = 7
  out_file = "data.txt"
  save_count = 100
  commonWeeks = [2,7] # RIGHT NOW THIS NEEDS TO BE CHANGED EVERY WEEK!!!
  weekOrder = generateWeekOrder(commonWeeks, nweeks)

  expire_dates= [ (1573171200 + 604800*(i - 1)) for i in weekOrder ]

  curr_url = ("https://www.marketwatch.com/investing/stock/" + stock.lower()).replace("\x00","")
  curr_html = urllib.request.urlopen(curr_url, context = ssl.SSLContext()).read()
  curr_soup = BeautifulSoup(curr_html, "html5lib")
  curr_price = tof(curr_soup.find("bg-quote", field="Last"))

  isRareStock = stock in rare_stocks

  if curr_price < price_max:
    for date_i in range(len(expire_dates)):
      w = weekOrder[date_i]
      if isRareStock and w not in commonWeeks:
        continue
      url = "http://finance.yahoo.com/quote/" + stock + "/options?p=" + stock + "&date=" + str(expire_dates[date_i])
      trows = []
      try:
        html = urllib.request.urlopen(url, context = ssl.SSLContext()).read()

        soup = BeautifulSoup(html, "html5lib")
        trows = soup.find("table", class_="calls").contents[1].children
      except Exception as e:
        print("Error getting data for " + stock + " on week " + str(w) + ":" + str(e))
        if (str(e) == "HTTP Error 404: Not Found"):
            return
        if w not in commonWeeks and (w == 1 or w == 2):
          isRareStock = True
          fp = open("rare_stocks.txt","a")
          fp.write(stock + "\n")
          fp.close()
        if w == min(commonWeeks):
            ptr = open("bad_stocks.txt", "a")
            ptr.write(stock + "\n")
            ptr.close()
            break
        pass

      for row in trows:
        last_date = row.contents[1].string
        strike = tof(row.contents[2].contents[0])
        last_price = tof(row.contents[3])
        bid = tof(row.contents[4])
        ask = tof(row.contents[5])
        volume = toi(row.contents[8])

        if volume > volume_min:
          profit_b = bid / w
          profit_a = ask / w
          profit_l = last_price / w
          in_mon = False

          if strike <= curr_price:
            profit_b = (bid + strike - curr_price) / w
            profit_a = (ask + strike - curr_price) / w
            profit_l = (last_price + strike - curr_price) / w
            in_mon = True

          e_b = profit_b / (curr_price)
          e_a = profit_a / (curr_price)
          e_l = profit_l / (curr_price)

          break_even = last_price / (curr_price * w)

          data = { "in_money": in_mon, "stock": stock, "curr_price": curr_price, "week": w, "expiration_date": expire_dates[date_i], "strike": strike,
                        "last_price": last_price, "bid": bid, "ask": ask, "volume": volume,
                        "profit_a": profit_a, "profit_b": profit_b, "profit_l": profit_l,
                        "e_b": e_b, "e_a": e_a, "e_l": e_l, "break_even": break_even }

          fp = open("data_parallel.txt", "a")
          fp.write(json.dumps(data) + "\n")
          fp.close()
    print("Processed " + stock)
  else:
    print("Too high price for " + stock)
  print("")

with Pool(3) as p:
  p.map(get_stock, stocks)
  print("Pooled")

print("--- %s seconds ---" % (time.time() - start_time))
