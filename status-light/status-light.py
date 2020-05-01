# https://github.com/portableprogrammer/Status-Light/

import webex
import os
import time
from datetime import datetime

# TODO: We're using the Webex status globally here, both because it's not bad, and because it was the first module created...
currentStatus = webex.PersonStatus.unknown
lastStatus = currentStatus

print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Startup")

# TODO: Set the light to idle
# aiotuya.set()

try:
    while True:
        # Webex Status
        personID = os.environ['WEBEX_PERSONID']
        webexAPI = webex.WebexAPI()
        webexAPI.botKey = os.environ['WEBEX_BOTID']
        webexStatus = webexAPI.getPersonStatus(personID)

        # TODO: O365 Status (based on calendar)

        # Take the statii and determine what we care about most
        # White/Green/Off when available
        # Blue when in a meeting (Calendar)
        # Red when on a call or DnD (due to the way that Teams handles status priorities) - This takes priority over calendar

        # TODO: Set the Calendar first, then let Webex override it

        if webexStatus != currentStatus:
            lastStatus = currentStatus
            currentStatus = webexStatus
            # TODO: Trigger light change

            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),currentStatus)

        # Sleep for a few seconds    
        time.sleep(15)
except KeyboardInterrupt:
    pass
except BaseException as e:
    print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),'Exception: ',e)

print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),'Shutdown')
# TODO: Trigger light shutdown