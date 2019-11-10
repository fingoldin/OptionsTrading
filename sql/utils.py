import time
import math

def generate_week_order(weeks, total_weeks):
    lst = []
    for i in weeks:
        if (i <= total_weeks and i > 0):
            lst.append(i)
    for i in range(1,total_weeks+1):
        if i not in lst:
            lst.append(i)
    return lst

def get_first_expiration():
  week_time = 604800
  week_offset = 86400
  utc = week_time * int(math.ceil((int(time.time()) - week_offset) / week_time)) + week_offset

  return utc

def get_manual_params():
  nweeks = 7
  common_weeks = [1,6] # RIGHT NOW THIS NEEDS TO BE CHANGED EVERY WEEK!!!
  volume_min = 10

  return nweeks, common_weeks, volume_min

def clean(v):
  return v.replace("-","0").replace(",","")

def toi(v):
  return int(clean(v.string))

def tof(v):
  return float(clean(v.string))

def log(s):
  print(s)

def utc_timestamp():
  return int(time.time())