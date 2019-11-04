import urllib.request
from bs4 import BeautifulSoup
import sys
import ssl
import json
import time

out_file = "data.txt"

strings = []
strings.extend(open("data_parallel.txt", "r", encoding="ascii").read().split("\n"))

data = []
for string in strings:
    if (len(string) > 0):
        data.append(json.loads(string))

file = open(out_file, "w")

priority_stocks = []
priority_stocks.extend(open("priority_ebid_stocks.txt", "r", encoding="ascii").read().split("\n"))

def write_priority(stock):
    filep = open("priority_ebid_stocks.txt", "a")
    filep.write(stock + "\n")
    filep.close()

data.sort(key=lambda x: x["e_b"])
for (i, st) in enumerate(data[::-1]):
    if (i <= 20 and st["stock"] not in priority_stocks):
        priority_stocks.append(st["stock"])
        write_priority(st["stock"])
    inString = "In" if st["in_money"] else "Out"
    # st["break_half"] = st["profit_l"] / st["last_price"]
    file.write("%d. STOCK NAME (%s): %s --- STOCK CURRENT PRICE: %.2f --- STRIKE: %.2f --- EXPIRATION DATE: %d --- BID: %.2f --- ASK: %.2f --- LAST PRICE: %.2f --- EBID: %.4f --- EASK: %.4f --- ELAST: %.4f --- BREAK EVEN BID: %.4f \n \n" % (i+1, inString, st["stock"], st["curr_price"], st["strike"], st["week"], st["bid"], st["ask"], st["last_price"],st["e_b"], st["e_a"], st["e_l"],st["break_even"]))

file.close()
