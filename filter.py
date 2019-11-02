import urllib.request
import sys
from bs4 import BeautifulSoup

in_fname = "nasdaq.txt"
out_fname = "nasdaq_clean.txt"
price_max = 7.00

prev_stocks = []
try:
  prev_stocks = open(out_fname, "r").read().split("\n")[:-1]
except:
  pass

def clean(v):
  return v.replace("-","0").replace(",","")

def toi(v):
  return int(clean(v.string))

def tof(v):
  return float(clean(v.string))

lines = open(in_fname, "r").read().split("\n")[:-1]
output = open(out_fname, "a")

for line in lines[1:]:
  stock = line.split("\t")[0]

  if not prev_stocks or stock > prev_stocks[-1]:
    try: 
      curr_url = "https://www.marketwatch.com/investing/stock/" + stock.lower()
      curr_html = urllib.request.urlopen(curr_url).read() 
      curr_soup = BeautifulSoup(curr_html, "html5lib")
      curr_price = tof(curr_soup.find("bg-quote", field="Last"))

      if curr_price < price_max:
        output.write(stock + "\n")
        output.flush()
        print(stock + " added")
      else:
        print(stock + " too expensive")
    except KeyboardInterrupt:
      output.close()
      sys.exit(0)
    except:
      print("Error on " + stock)
      pass
  else:
    print(stock + " skipped")

output.close()
