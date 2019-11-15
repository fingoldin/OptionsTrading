from .sql import SQL
from .utils import utc_timestamp

def get_options(stock):
    with SQL() as c:
        data = c.get("SELECT * FROM options WHERE stock IN (SELECT id from stocks where name=\"" + str(stock) + "\")")
    return data

def get_option_data(option):
  with SQL() as c:
    data = c.get("SELECT * FROM options WHERE id=\"" + str(option) + "\"")

  return data

def get_stock_name(id):
    name = ""
    with SQL() as c:
        name = c.get("SELECT * from stocks WHERE id=\"" + str(id) + "\"")
    if (len(name) > 0):
        return name[0]["name"]
    else:
        return ""

# time is in minutes
def get_recent_options(time=100):
    with SQL() as c:
        data = c.get("SELECT * FROM options WHERE timestamp>\"" + str(utc_timestamp() - time * 60) + "\"")
        for opt in data:
            name = get_stock_name(opt["stock"])
            opt["name"] = name
    return data

def get_prices(stock):
  with SQL() as c:
    data = c.get("SELECT * FROM stock_prices WHERE stock IN (SELECT id from stocks where name=\"" + str(stock) + "\")")

  return data

def get_all_stocks():
  with SQL() as c:
    data = c.get("SELECT * FROM stocks")
  return data
