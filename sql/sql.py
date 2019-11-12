import MySQLdb
import MySQLdb.cursors

class SQL:
  def __enter__(self):
    self.conn = MySQLdb.Connect("localhost","local","options","stocks", cursorclass=MySQLdb.cursors.DictCursor)
    self.cursor = self.conn.cursor()
    return self

  def get(self, query):
    self.cursor.execute(query)
    return list(self.cursor.fetchall())

  def set(self, query, params):
    self.cursor.execute(query, params)
    return self.conn.commit()

  def __exit__(self, etype, value, tb):
    self.conn.close()
    return False

  def lastid():
    return self.conn.insert_id()

def sql_get_stocks():
  with SQL() as c:
    data = c.get("SELECT * FROM stocks")

  return data

def sql_save_stock(stock, timestamp, price):
  with SQL() as c:
    c.set("INSERT INTO stock_prices SET insert_time=NOW(),stock=%d,timestamp=%d,price=%f",
           (stock, timestamp, price))

def sql_save_option(data):
  option_meta = tuple([ v for v in data["option"].values() ])
  option_data = [ v for v in data["option"].values() ]
  with SQL() as c:
    r = c.get("SELECT FROM options WHERE stock=%d,expiration_date=%d,strike=%f,put=%d", option_meta)
    if r:
      option_id = r["id"]
    else:
      s.set("INSERT INTO options SET stock=%d,expiration_date=%d,strike=%f,put=%d", option_meta)
      option_id = c.lastid()
      
    option_data.insert(0, option_id)
    c.set("""INSERT INTO option_data SET insert_time=NOW(), option_id=%d, timestamp=%d,
             curr_price=%f, last_price=%f, bid=%f, ask=%f, volume=%d, e_b=%f,
             e_a=%f, e_l=%f, break_even=%f, volatility=%f""", tuple(option_data))
  
def sql_save_options(options):
  for option in options:
    sql_save_option(option)
