#!/usr/bin/env python

# regmeet date [group_urlname]

import meetup_api_client as meetup

import datetime
import time
import sys
import os

import smtplib
from email.mime.text import MIMEText

# turn off output buffering
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

if len(sys.argv) > 3:
  print 'usage: regmeet [date [group_urlname]]'
  sys.exit(4)

def notify(subject):
  print 'EMAIL NOTIFICATION:', subject

  msg = MIMEText("so long")
  msg['Subject'] = '[RegMeet] ' + subject
  msg['From'] = 'laufer@cs.luc.edu'
  msg['To'] = 'laufer@cs.luc.edu'

  s = smtplib.SMTP('smtp.rcn.com')
  s.sendmail(msg['From'], msg['To'], msg.as_string())
  s.quit()

# default settings
sleep_time = 120 # seconds
meetup_api_key = '7e3e2142282f42752f3517334f7c304'
group_urlname = 'sc-chicago'
date_as_string = datetime.datetime.now().strftime('%m%d%Y')

# command-line arguments
if len(sys.argv) >= 2:
  date_as_string = sys.argv[1]
if len(sys.argv) == 3:
  group_urlname = sys.argv[2]

meetup = meetup.Meetup(meetup_api_key)
event_date = datetime.datetime.strptime(date_as_string, '%m%d%Y').toordinal()
before_as_string = datetime.date.fromordinal(event_date + 1).strftime('%m%d%Y')

# look for events
while True:

  # check for events on the desired date
  events = meetup.get_events(group_urlname=group_urlname, 
             after=date_as_string, before=before_as_string)
  if len(events.results) > 0:
    print 'found', len(events.results), 'event(s)'
    break

  # next line for for testing only
  # now = datetime.datetime.strptime(date_as_string, '%m%d%Y')

  # give up if we have waited until the desired date
  now = datetime.datetime.now()
  now_as_ordinal = now.toordinal()
  if now_as_ordinal >= event_date:
    notify('No events have been scheduled by the target date, giving up')
    sys.exit(1)

  # sleep briefly and try again
  time.sleep(sleep_time)

# try to sign up for the events
failures = False
for event in events.results:
  try:
    meetup.post_rsvp(rsvp='yes', event_id=event.id, comments='Yay!!! My bot signed me up :-]')
    notify('You are registered for ' + event.name)
  except Exception:
    failures = True
    notify('No more spots left for ' + event.name)

if failures:
  sys.exit(2)
