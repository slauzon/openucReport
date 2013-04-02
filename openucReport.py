#!/usr/bin/env python

import datetime
import psycopg2
import sys
import socket

today = datetime.date.today()
margin = datetime.timedelta(days = 5)

def logins(today,margin):
  loginCount = 0
  for line in open('/var/log/sipxpbx/sipxconfig-logins.log').readlines():
    timestamp,info = line.strip().split(': ')
    timestamp = timestamp.replace('"','').split(',')[0]
    date_object = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    if today - margin <= date_object.date() <= today:
      #print(str(date_object) + ' ' + info)
      loginCount += 1
  return loginCount

def calls(date):
  try:
    con = psycopg2.connect(database='SIPXCDR', user='postgres')
    cur = con.cursor()
    cur.execute("SELECT call_id FROM cdrs WHERE start_time >= '%s';" % date)
    return cur.rowcount
  except psycopg2.DatabaseError, e:
    print 'Error %s' % e
    sys.exit(1)
  finally:
    if con:
      con.close()

print('Statistics for %s openUC Trial' % socket.gethostname())
print('Logins since %s:  %s' % (today - margin,logins(today,margin)))
print('Calls since %s:  %s' % (today - margin,calls(today - margin)))
