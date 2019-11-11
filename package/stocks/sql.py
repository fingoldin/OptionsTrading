import MySQLdb
import MySQLdb.cursors

class SQL:
  def __enter__(self):
    self.conn = MySQLdb.Connect("34.227.25.58","remote","options","stocks", cursorclass=MySQLdb.cursors.DictCursor)
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
