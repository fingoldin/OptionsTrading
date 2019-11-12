import MySQLdb
import MySQLdb.cursors

class SQL:
  def __enter__(self):
    self.conn = MySQLdb.Connect("localhost","local","options","stocks", cursorclass=MySQLdb.cursors.DictCursor)
    self.cursor = self.conn.cursor()
    return self

  def get(self, query, params=None):
    self.cursor.execute(query, params)
    return list(self.cursor.fetchall())

  def set(self, query, params=None):
    self.cursor.execute(query, params)
    return self.conn.commit()

  def __exit__(self, etype, value, tb):
    self.conn.close()
    return False

  def lastid(self):
    return self.conn.insert_id()

def sql_get_stocks():
  with SQL() as c:
    data = c.get("SELECT * FROM stocks")

  return data

def sql_save_stock(stock, timestamp, price):
  with SQL() as c:
    c.set("INSERT INTO stock_prices SET insert_time=NOW(),stock=%s,timestamp=%s,price=%s",
           (stock, timestamp, price))

def sql_save_option(data):
  option_meta = tuple([ v for v in data["option"].values() ])
  option_data = [ v for v in data["data"].values() ]
  with SQL() as c:
    r = c.get("SELECT id FROM options WHERE stock=%s AND expiration=%s AND strike=%s AND put=%s", option_meta)
    if r:
      option_id = r[0]["id"]
    else:
      c.set("INSERT INTO options SET stock=%s,expiration=%s,strike=%s,put=%s", option_meta)
      option_id = c.lastid()
      
    option_data.insert(0, option_id)
    c.set("""INSERT INTO option_data SET insert_time=NOW(), option_id=%s, timestamp=%s,
             curr_price=%s, last_price=%s, bid=%s, ask=%s, volume=%s, e_b=%s,
             e_a=%s, e_l=%s, break_even=%s, volatility=%s""", tuple(option_data))
  
def sql_save_options(options):
  for option in options:
    sql_save_option(option)
