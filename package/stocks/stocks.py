from .sql import SQL

def get_options(stock):
  data = []
  with SQL() as c:
    data = c.get("SELECT * FROM options WHERE stock IN (SELECT id from stocks where name=\"" + str(stock) + "\")")

  return data
