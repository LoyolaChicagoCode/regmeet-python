#!/usr/bin/env python

# regmeet [MMDDYYYY [number_of_events [group_urlname]]]

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

# check usage
if len(sys.argv) > 4:
  print 'usage: regmeet [MMDDYYYY [number_of_events [group_urlname]]]'
  sys.exit(4)

# encapsulate notification method here
def notify(subject, body=''):
  print 'EMAIL NOTIFICATION:', subject

  msg = MIMEText(body)
  msg['Subject'] = '[RegMeet] ' + subject
  msg['From'] = 'laufer@cs.luc.edu'
  msg['To'] = 'laufer@cs.luc.edu'

  s = smtplib.SMTP('smtp.rcn.com')
  s.sendmail(msg['From'], msg['To'], msg.as_string())
  s.quit()

# configuration settings 
sleep_time = 120 # seconds
meetup_api_key = '7e3e2142282f42752f3517334f7c304'

# default settings for command-line arguments
group_urlname = 'sc-chicago'
date_as_string = datetime.datetime.now().strftime('%m%d%Y')
number_of_events = 1

# process command-line arguments
if len(sys.argv) >= 2:
  date_as_string = sys.argv[1]
if len(sys.argv) == 3:
  number_of_events = int(sys.argv[2])
if len(sys.argv) == 4:
  group_urlname = sys.argv[3]

# variables
meetup = meetup.Meetup(meetup_api_key)
event_date = datetime.datetime.strptime(date_as_string, '%m%d%Y').toordinal()
before_as_string = datetime.date.fromordinal(event_date + 1).strftime('%m%d%Y')
event_ids_processed = []
failures = False

# look for at least the specified number of events
while True:

  now = datetime.datetime.now()

  # check for events on the desired date
  print now.strftime('%a %d %b %Y %H:%M'),
  events = meetup.get_events(group_urlname=group_urlname, 
             after=date_as_string, before=before_as_string)
  
  # try to sign up for any unseen events
  for event in events.results:
    if event.id not in event_ids_processed:
      event_ids_processed.append(event.id)
      try:
        meetup.post_rsvp(rsvp='yes', 
                         event_id=event.id, 
                         comments='Yay!!! My bot signed me up :-]')
        notify('You are registered for ' + event.name, str(event))
      except Exception:
        failures = True
        notify('No more spots left for ' + event.name, str(event))

  if len(event_ids_processed) >= number_of_events:
    break

  # give up if we have waited until the desired date
  if now.toordinal() >= event_date:
    notify('No events have been scheduled by the target date, giving up')
    sys.exit(1)

  # sleep briefly and try again
  time.sleep(sleep_time)

if failures:
  sys.exit(2)
