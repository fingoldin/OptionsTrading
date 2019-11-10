from .sql import SQL
from .utils import utc_timestamp

def get_options(stock):
  data = []
  with SQL() as c:
    data = c.get("SELECT * FROM options WHERE stock IN (SELECT id from stocks where name=\"" + str(stock) + "\")")

  return data

# time is in minutes 
def get_recent_options(time=100):
  data = []
  with SQL() as c:
    data = c.get("SELECT * FROM options WHERE timestamp>\"" + str(utc_timestamp() - time * 60) + "\"")

  return data
