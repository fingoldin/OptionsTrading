import urllib.request
from bs4 import BeautifulSoup
import sys
import ssl
import json
import time

start_time = time.time()

stocks_files = ["nasdaq_clean.txt", "nyse_clean.txt"]
price_max = 7.00
volume_min = 10
nweeks = 8
out_file = "data.txt"
save_count = 100
commonWeeks = [2,7,11] # this one week per month

expire_dates= [ (1573171200 + 604800*i) for i in range(nweeks) ]

stocks = []
bad_stocks = []
bad_stocks.extend(open("bad_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])
rare_stocks = []
rare_stocks.extend(open("rare_stocks.txt", "r", encoding="ascii").read().split("\n")[:-1])


for stocks_file in stocks_files:
  stocks.extend(open(stocks_file, "r", encoding="ascii").read().split("\n")[:-1])

stocks = [s.replace("\x00","") for s in stocks]
stocks = [s for s in stocks if s not in bad_stocks]
stocks.sort()

def clean(v):
  return v.replace("-","0").replace(",","")

def toi(v):
  return int(clean(v.string))

def tof(v):
  return float(clean(v.string))

def checker(data1, data2):
    if (len(data1) != len(data2)):
        return False
    for i in range(len(data1)):
        if (data1[i]["stock"] != data2[i]["stock"] or data1[i]["strike"] != data2[i]["strike"]):
            return False
    return True

data = []
previous = []

try:
  for stock in stocks:
    curr_url = ("https://www.marketwatch.com/investing/stock/" + stock.lower()).replace("\x00","")
    curr_html = urllib.request.urlopen(curr_url, context = ssl.SSLContext()).read()
    curr_soup = BeautifulSoup(curr_html, "html5lib")
    curr_price = tof(curr_soup.find("bg-quote", field="Last"))

    failedOnNotCommon = stock in rare_stocks

    if curr_price < price_max:
      for date_i in range(len(expire_dates)):
        w = date_i + 1
        if failedOnNotCommon and w not in commonWeeks:
          continue
        url = "http://finance.yahoo.com/quote/" + stock + "/options?p=" + stock + "&date=" + str(expire_dates[date_i])
        trows = []
        try:
          html = urllib.request.urlopen(url, context = ssl.SSLContext()).read()

          soup = BeautifulSoup(html, "html5lib")
          trows = soup.find("table", class_="calls").contents[1].children
        except:
          print("Error getting data for " + stock + " on week " + str(w) + "\n")
          if w not in commonWeeks and (w == 1 or w == 2):
            failedOnNotCommon = True
            fil = open("rare_stocks.txt", "a")
            fil.write(stock + "\n")
            fil.close()
          if w in commonWeeks:
            if (failedOnNotCommon):
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

            break_even = last_price / curr_price

            data.append({ "in_money": in_mon, "stock": stock, "curr_price": curr_price, "week": w, "expiration_date": expire_dates[date_i], "strike": strike,
                          "last_price": last_price, "bid": bid, "ask": ask, "volume": volume,
                          "profit_a": profit_a, "profit_b": profit_b, "profit_l": profit_l,
                          "e_b": e_b, "e_a": e_a, "e_l": e_l, "break_even": break_even })

            data.sort(key=lambda x: x["e_b"])
            if (len(data) <= save_count):
                  temp = open(out_file, "w")
                  temp.write("")
                  temp.close()
                  for (index,st) in enumerate(data[::-1]):
                      file = open(out_file, "a")
                      inString = "In" if st["in_money"] else "Out"
                      file.write("%d. STOCK NAME (%s): %s --- STOCK CURRENT PRICE: %.2f --- STRIKE: %.2f --- EXPIRATION DATE: %d --- BID: %.2f --- ASK: %.2f --- LAST PRICE: %.2f --- EBID: %.4f --- EASK: %.4f --- ELAST: %.4f --- BREAK EVEN BID: %.4f \n \n" % (index+1, inString, st["stock"], st["curr_price"], st["strike"], st["week"], st["bid"], st["ask"], st["last_price"],st["e_b"], st["e_a"], st["e_l"],st["break_even"]))
                      file.close()
                  previous = data
            else:
                if (not checker(previous, data[-save_count:])):
                    temp = open(out_file, "w")
                    temp.write("")
                    temp.close()
                    for (index,st) in enumerate(data[-save_count:][::-1]):
                        file = open(out_file, "a")
                        inString = "In" if st["in_money"] else "Out"
                        file.write("%d. STOCK NAME (%s): %s --- STOCK CURRENT PRICE: %.2f --- STRIKE: %.2f --- EXPIRATION DATE: %d --- BID: %.2f --- ASK: %.2f --- LAST PRICE: %.2f --- EBID: %.4f --- EASK: %.4f --- ELAST: %.4f --- BREAK EVEN BID: %.4f \n \n" % (index+1, inString, st["stock"], st["curr_price"], st["strike"], st["week"], st["bid"], st["ask"], st["last_price"],st["e_b"], st["e_a"], st["e_l"],st["break_even"]))
                        file.close()
                    previous = data[-save_count:]
            # json.dump(data[-save_count:], open(out_file, "w")) - OLD FILE WRITING MECHANISM

      print("Processed " + stock)
      if data:
        data.sort(key=lambda x: x["e_b"])
        m = "In" if data[-1]["in_money"] else "Out"
        print("Best %s e_bid: %f, stock: %s, strike price: %f, bid: %f, curr_price: %f, expire_weeks: %d, break_even: %f" % (m, data[-1]["e_b"], data[-1]["stock"], data[-1]["strike"], data[-1]["bid"], data[-1]["curr_price"], data[-1]["week"], data[-1]["break_even"]))

        data.sort(key=lambda x: x["e_a"])
        m = "In" if data[-1]["in_money"] else "Out"
        print("Best %s e_ask: %f, stock: %s, strike price: %f, ask: %f, curr_price: %f, expire_weeks: %d, break_even: %f" % (m, data[-1]["e_a"], data[-1]["stock"], data[-1]["strike"], data[-1]["ask"], data[-1]["curr_price"], data[-1]["week"], data[-1]["break_even"]))

        data.sort(key=lambda x: 0.5*(x["e_a"]+x["e_b"]))
        m = "In" if data[-1]["in_money"] else "Out"
        print("Best %s e_mean: %f, stock: %s, strike price: %f, mean: %f, curr_price: %f, expire_weeks: %d, break_even: %f" % (m, 0.5*(data[-1]["e_a"]+data[-1]["e_b"]), data[-1]["stock"], data[-1]["strike"], 0.5*(data[-1]["bid"]+data[-1]["ask"]), data[-1]["curr_price"], data[-1]["week"], data[-1]["break_even"]))

        data.sort(key=lambda x: x["e_l"])
        m = "In" if data[-1]["in_money"] else "Out"
        print("Best %s e_last: %f, stock: %s, strike price: %f, last: %f, curr_price: %f, expire_weeks: %d, break_even: %f" % (m, data[-1]["e_l"], data[-1]["stock"], data[-1]["strike"], data[-1]["last_price"], data[-1]["curr_price"], data[-1]["week"], data[-1]["break_even"]))
      else:
        print("No data")
    else:
      print("Too high price for " + stock)
    print("")
except KeyboardInterrupt:
  temp = open(out_file, "w")
  temp.write("")
  temp.close()
  save_count = min(save_count, len(data))
  for (index,st) in enumerate(data[-save_count:][::-1]):
    file = open(out_file, "a")
    inString = "In" if st["in_money"] else "Out"
    file.write("%d. STOCK NAME (%s): %s --- STOCK CURRENT PRICE: %.2f --- STRIKE: %.2f --- EXPIRATION DATE: %d --- BID: %.2f --- ASK: %.2f --- LAST PRICE: %.2f --- EBID: %.4f --- EASK: %.4f --- ELAST: %.4f --- BREAK EVEN BID: %.4f \n \n" % (index+1, inString, st["stock"], st["curr_price"], st["strike"], st["week"], st["bid"], st["ask"], st["last_price"],st["e_b"], st["e_a"], st["e_l"],st["break_even"]))
    file.close()
  # json.dump(data[-save_count:], open(out_file, "w"))  -- OLD FILE WRITE
  print("--- %s seconds ---" % (time.time() - start_time))
  pass
print("--- %s seconds ---" % (time.time() - start_time))
