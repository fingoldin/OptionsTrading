import MySQLdb
import MySQLdb.cursors

class SQL:
  def __enter__(self):
    self.conn = MySQLdb.Connect("localhost","vassy","","stocks", cursorclass=MySQLdb.cursors.DictCursor)
    self.cursor = self.conn.cursor()
    return self

  def get(self, query):
    self.cursor.execute(query)
    return self.cursor.fetchall()

  def set(self, query):
    self.cursor.execute(query)
    return self.conn.commit()

  def __exit__(self, etype, value, tb):
    self.conn.close()
    return False

def sql_get_stocks():
  with SQL() as c:
    data = c.get("SELECT * FROM stocks")

  return data

def sql_save_stock(stock, timestamp, price):
  with SQL() as c:
    c.set("INSERT INTO stock_prices VALUES (DEFAULT," + \
          str(stock) + "," + str(timestamp) + "," + str(price) + ")")

def sql_save_option(data):
  data_str = ",".join([ str(v) for v in data.values() ])

  with SQL() as c:
    c.set("INSERT INTO options VALUES (DEFAULT,DEFAULT," + data_str + ")")
  
def sql_save_options(options):
  for option in options:
    sql_save_option(option)
