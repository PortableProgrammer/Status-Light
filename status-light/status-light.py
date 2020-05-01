#!/usr/bin/python
# https://github.com/portableprogrammer/Status-Light/

import webex
import os
import time

try:
    while True:
        # Webex Status
        personID = os.environ['WEBEX_PERSONID']
        webexAPI = webex.WebexAPI()
        webexAPI.botKey = os.environ['WEBEX_BOTID']
        webexStatus = webexAPI.getPersonStatus(personID)

        # O365 Status (based on calendar)

        # Take the statii and determine what we care about most
        # White/Green/Off when available
        # Blue when in a meeting (Calendar)
        # Red when on a call or DnD (due to the way that Teams handles status priorities) - This takes priority over calendar

        # Set the Calendar first, then let Webex override it

        print(webexStatus)
        time.sleep(15)

except:
    print('Exception!')
