#!/usr/bin/env python

import datetime
import psycopg2
import sys
import socket
import glob
import gzip

launchDate = '2013-03-17'
today = datetime.date.today()
margin = datetime.timedelta(days = 5)
marginDay = today - margin

def logins(today,margin):
  weekLogins = 0
  totalLogins = 0
  for files in glob.glob('/var/log/sipxpbx/sipxconfig-logins*'):
    if files.endswith('.gz'):
      data = gzip.open(files, 'rb')
    else:
      data = open(files)
    for line in data.readlines():
      timestamp,info = line.strip().split(': ')
      timestamp = timestamp.replace('"','').split(',')[0]
      date_object = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
      if today - margin <= date_object.date() <= today:
	#print(str(date_object) + ' ' + info)
	weekLogins += 1
	totalLogins += 1
      else: 
	totalLogins += 1
  return weekLogins,totalLogins

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
weekLogins, totalLogins = logins(today,margin)

output = '''
HOSTNAME Usage Report
------
Logins since launch date LAUNCHDAY:	TOTALLOGINS
Logins since MARGINDAY:		WEEKLOGINS
Calls since launch date LAUNCHDAY:	TOTALCALLS
Calls since MARGINDAY:			WEEKCALLS
'''

output = output.replace('HOSTNAME', socket.gethostname())
output = output.replace('LAUNCHDAY', launchDate).replace('MARGINDAY', str(marginDay))
output = output.replace('TOTALLOGINS', str(totalLogins)).replace('WEEKLOGINS', str(weekLogins))
output = output.replace('TOTALCALLS', str(calls(launchDate))).replace('WEEKCALLS', str(calls(marginDay)))

print(output)
