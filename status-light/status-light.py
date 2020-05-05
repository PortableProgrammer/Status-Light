# https://github.com/portableprogrammer/Status-Light/

# Module imports
import os
import time
from datetime import datetime

# Project imports
import webex
import tuya

# TODO: We're using the Webex status globally here, both because it's not bad, and because it was the first module created...
currentStatus = webex.PersonStatus.unknown
lastStatus = currentStatus

print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Startup")

# TODO: Set the light to idle
light = tuya.TuyaLight()
light.device = eval(os.environ['TUYA_DEVICE'])

print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Turning light on")
light.on()
print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Transitioning to a random color at a random brightness")
import random
brightness = random.randint(32,128)
print("    Random brightness: ", brightness)
colors = [ "ff00000000ffff", "00ff000000ffff", "0000ff0000ffff" ]
color = colors[random.randint(0,2)]
print("    Random color: ", color)    
#result = light.transitionTo(eval("{ '1': 1, '2': 'colour', '3': " + str(brightness) + ", '5': '" + color + "' }"))
#print(" Transition result: ", result)
#light.setState(2, 'colour')
#light.setState(3, brightness)
#light.setState(5, color)

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

print("\n",datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),'Shutdown')
# TODO: Trigger light shutdown
print("    Turning light off")
light.off()