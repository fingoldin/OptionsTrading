import time
import datetime
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
  return v.replace("-","0").replace(",","").replace("%","")

def log(s):
  fp = open("/home/ec2-user/OptionsTrading/sql/log.txt","a")
  fp.write("[" + str(datetime.datetime.now()) + "]: " + s + "\n")
  fp.close()
  print(s)

def toi(c, i):
  try:
    ret = int(clean(c[i].string))
  except Exception as e:
    log("Error in toi for " + str(c) + " on index " + str(i))
    ret = -1
    pass

  return ret

def tof(c, i):
  try:
    ret = float(clean(c[i].string))
  except Exception as e:
    log("Error in tof for " + str(c) + " on index " + str(i))
    ret = -1.0
    pass

  return ret

def tos(c, i):
  try:
    ret = c[i].string
  except Exception as e:
    log("Error in tos for " + str(c) + " on index " + str(i))
    ret = "null"
    pass

  return ret

def utc_timestamp():
  return int(time.time())
