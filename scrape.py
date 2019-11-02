import urllib.request
from bs4 import BeautifulSoup
import sys
import json

stocks_file = "stocks.txt"
price_max = 7.00
volume_min = 10
expire_dates= [1573171200, 1573776000]
out_file = "data.json"
save_count = 20


stocks = open(stocks_file).read().split("\n")[:-1]

def clean(v):
  return v.replace("-","0").replace(",","")

def toi(v):
  return int(clean(v.string))

def tof(v):
  return float(clean(v.string))

data = []

try: 
  for stock in stocks:
    curr_url = "https://www.marketwatch.com/investing/stock/" + stock.lower()
    curr_html = urllib.request.urlopen(curr_url).read() 
    curr_soup = BeautifulSoup(curr_html, "html5lib")
    curr_price = tof(curr_soup.find("bg-quote", field="Last"))

    if curr_price < price_max:
      for date_i in range(len(expire_dates)):
        w = date_i + 1
        url = "http://finance.yahoo.com/quote/" + stock + "/options?p=" + stock + "&date=" + str(expire_dates[date_i])
        trows = []
        try:
          html = urllib.request.urlopen(url).read()

          soup = BeautifulSoup(html, "html5lib")
          trows = soup.find("table", class_="calls").contents[1].children
        except AttributeError:
          print("Error getting data for " + stock + "\n")
          pass

        for row in trows:
          last_date = row.contents[1].string
          strike = tof(row.contents[2].contents[0])
          last_price = tof(row.contents[3])
          bid = tof(row.contents[4])
          ask = tof(row.contents[5])
          volume = toi(row.contents[8])

          if strike <= curr_price and volume > volume_min:
            profit_b = bid + strike - curr_price
            profit_a = ask + strike - curr_price
            profit_l = last_price + strike - curr_price
            e_b = profit_b / (w*curr_price)
            e_a = profit_a / (w*curr_price)
            e_l = profit_l / (w*curr_price)

            data.append({ "stock": stock, "curr_price": curr_price, "expiration_date": expire_dates[date_i], "strike": strike, 
                          "last_price": last_price, "bid": bid, "ask": ask, "volume": volume, 
                          "profit_a": profit_a, "profit_b": profit_b, "profit_l": profit_l,
                          "e_b": e_b, "e_a": e_a, "e_l": e_l })

      print("Processed " + stock)
      if data:
        data.sort(key=lambda x: x["e_b"])
        print("Best e_bid: %f, stock: %s, strike price: %f, bid: %f, curr_price: %f, expire_weeks: %d" % (data[-1]["e_b"], data[-1]["stock"], data[-1]["strike"], data[-1]["bid"], data[-1]["curr_price"], w))

        data.sort(key=lambda x: x["e_a"])
        print("Best e_ask: %f, stock: %s, strike price: %f, ask: %f, curr_price: %f, expire_weeks: %d" % (data[-1]["e_a"], data[-1]["stock"], data[-1]["strike"], data[-1]["ask"], data[-1]["curr_price"], w))

        data.sort(key=lambda x: 0.5*(x["e_a"]+x["e_b"]))
        print("Best e_mean: %f, stock: %s, strike price: %f, mean: %f, curr_price: %f, expire_weeks: %d" % (0.5*(data[-1]["e_a"]+data[-1]["e_b"]), data[-1]["stock"], data[-1]["strike"], 0.5*(data[-1]["bid"]+data[-1]["ask"]), data[-1]["curr_price"], w))
        
        data.sort(key=lambda x: x["e_l"])
        print("Best e_last: %f, stock: %s, strike price: %f, last: %f, curr_price: %f, expire_weeks: %d" % (data[-1]["e_l"], data[-1]["stock"], data[-1]["strike"], data[-1]["last_price"], data[-1]["curr_price"], w))
      else:
        print("No data")
    else:
      print("Too high price for " + stock)

    print("")
except KeyboardInterrupt:
  json.dump(data[-save_count:], open(out_file, "w"))
  pass
