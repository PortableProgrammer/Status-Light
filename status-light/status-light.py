# https://github.com/portableprogrammer/Status-Light/

# Module imports
import os
import time
from datetime import datetime

# Project imports
import webex
import office365
import tuya
import const

currentStatus = const.Status.unknown
lastStatus = currentStatus

print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Startup")

light = tuya.TuyaLight()
light.device = eval(os.environ['TUYA_DEVICE'])
light.transitionStatus(currentStatus)

# TODO: Test code, remove once comfortable
#print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Transitioning to a random color at a random brightness")
#import random
#brightness = random.randint(32,128)
#print("    Random brightness: ", brightness)
#colors = [ "ff00000000ffff", "00ff000000ffff", "0000ff0000ffff" ]
#color = colors[random.randint(0,2)]
#print("    Random color: ", color)    
#light.setSingleState(3, brightness)
#light.setSingleState(5, color)
#light.setSingleState(2, 'colour')
#print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),"Turning light on")
#light.on()

try:
    while True:
        # Webex Status
        personID = os.environ['WEBEX_PERSONID']
        webexAPI = webex.WebexAPI()
        webexAPI.botKey = os.environ['WEBEX_BOTID']
        webexStatus = webexAPI.getPersonStatus(personID)

        # TODO: O365 Status (based on calendar)
        officeAPI = office365.OfficeAPI()
        office365.appID = os.environ['O365_APPID']
        office365.appSecret = os.environ['O365_APPSECRET']
        
        # TODO: Compare statii and emerge a winner
        
        if webexStatus != currentStatus:
            lastStatus = currentStatus
            currentStatus = webexStatus

            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "),currentStatus)
            light.transitionStatus(currentStatus)

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
