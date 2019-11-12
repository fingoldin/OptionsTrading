import urllib.request
from bs4 import BeautifulSoup
import ssl
from multiprocessing import Pool
import utils
import sql

def scrape_price(stock):
  curr_url = ("https://www.marketwatch.com/investing/stock/" + stock["name"].lower()).replace("\x00","")
  
  timestamp = utils.utc_timestamp()

  try:
    curr_html = urllib.request.urlopen(curr_url, context = ssl.SSLContext()).read()
    curr_soup = BeautifulSoup(curr_html, "html5lib")
    curr_price = float(utils.clean(curr_soup.find("bg-quote", field="Last").string))
  except Exception as e:
    curr_price = -1.0
    utils.log("Error getting price for " + stock["name"] + ": " + str(e))
    #if (str(e) == "HTTP Error 404: Not Found"):
    #  return timestamp, -1.0

  return timestamp, curr_price

def scrape_options(stock):
  nweeks, common_weeks, volume_min = utils.get_manual_params()

  week_time = 604800
  first_expiration = utils.get_first_expiration()
  week_order = utils.generate_week_order(common_weeks, nweeks)
  expire_dates= [ (first_expiration + week_time*(i - 1)) for i in week_order ]

  out_data = []
  
  curr_stamp, curr_price = scrape_price(stock)

  if curr_price != -1.0:
    sql.sql_save_stock(stock["id"], curr_stamp, curr_price)

    for date_i in range(len(expire_dates)):
      w = week_order[date_i]
      if stock["rare"] and w not in common_weeks:
        continue
      url = "http://finance.yahoo.com/quote/" + stock["name"] + "/options?p=" + \
            stock["name"] + "&date=" + str(expire_dates[date_i])
      trows = []
      try:
        timestamp = utils.utc_timestamp()
        html = urllib.request.urlopen(url, context = ssl.SSLContext()).read()

        soup = BeautifulSoup(html, "html5lib")
        trows = soup.find("table", class_="calls").contents[1].children
        if not trows:
          raise ValueError("trows is None")
      except Exception as e:
        utils.log("Error getting data for " + stock["name"] + " on week " + str(w) + ":" + str(e))

      for row in trows:
        try:
          contents = row.contents
          if not contents:
            raise ValueError("contents is None")
        except Exception as e:
          utils.log("Error getting row data for " + stock["name"] + " on row: " + str(row))

        try:
          strike_cont = contents[2].contents
          if not strike_cont:
            raise ValueError("strike_cont is None")
        except Exception as e:
          utils.log("Error getting strike container for " + stock["name"] + " on row: " + str(row))

        last_date = utils.tos(contents, 1)
        strike = utils.tof(strike_cont, 0)
        last_price = utils.tof(contents, 3)
        bid = utils.tof(contents, 4)
        ask = utils.tof(contents, 5)
        volume = utils.toi(contents, 8)
        implied_volatility = utils.tof(contents, 10)

        if volume > volume_min:
          profit_b = bid / w
          profit_a = ask / w
          profit_l = last_price / w

          if strike <= curr_price:
            profit_b = (bid + strike - curr_price) / w
            profit_a = (ask + strike - curr_price) / w
            profit_l = (last_price + strike - curr_price) / w

          if curr_price != 0: 
            e_b = profit_b / (curr_price)
            e_a = profit_a / (curr_price)
            e_l = profit_l / (curr_price)
          else:
            e_b = 0.0
            e_a = 0.0
            e_l = 0.0

          break_even = last_price / (curr_price * w)
          
          # Don't change the order, name, or number of keys!
          data = {
                   "option": {
                     "stock": stock["id"], "expiration": expire_dates[date_i], 
                     "strike": strike, "put": 0
                    },
                   "data": {
                     "timestamp": timestamp, "curr_price": curr_price, 
                     "last_price": last_price, "bid": bid, "ask": ask, "volume": volume,
                     "e_b": e_b, "e_a": e_a, "e_l": e_l, "break_even": break_even,
                     "volatility": implied_volatility 
                    }
                  }

          out_data.append(data)
      utils.log("Processed " + stock["name"])

  return out_data

def scrape_and_save(stock):
  data = scrape_options(stock)

  sql.sql_save_options(data)

def scrape_and_save_all(pool_size):
  stocks = sql.sql_get_stocks()

  with Pool(pool_size) as p:
    p.map(scrape_and_save, stocks)
