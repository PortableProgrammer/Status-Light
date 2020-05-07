# https://github.com/portableprogrammer/Status-Light/

# Module imports
import os
import time
import logging
from datetime import datetime

# Project imports
import webex
import office365
import tuya
import const

currentStatus = const.Status.unknown
lastStatus = currentStatus

# TODO: Dynamic logging level
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.WARNING)
logger = logging.getLogger(__name__)

logger.info('Startup')
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Startup')

# TODO: Gather and validate environment variables in a structured way
# Webex
# Office365
# Tuya

light = tuya.TuyaLight()
light.device = eval(os.environ['TUYA_DEVICE'])
logger.debug('Retrieved TUYA_DEVICE variable: %s', light.device)

light.transitionStatus(currentStatus)

try:
    while True:
        # Webex Status
        personID = os.environ['WEBEX_PERSONID']
        webexAPI = webex.WebexAPI()
        webexAPI.botKey = os.environ['WEBEX_BOTID']
        webexStatus = webexAPI.getPersonStatus(personID)

        # O365 Status (based on calendar)
        officeAPI = office365.OfficeAPI()
        officeAPI.appID = os.environ['O365_APPID']
        officeAPI.appSecret = os.environ['O365_APPSECRET']
        officeAPI.authenticate()
        officeStatus = officeAPI.getCurrentStatus()
        
        # Compare statii and emerge a winner
        logger.debug('Webex: %s | Office: %s', webexStatus, officeStatus)

        # Webex status always wins except in specific scenarios
        currentStatus = webexStatus

        # If we're "GREEN" or "OFF" for Webex, but not Office, use the office status
        if (webexStatus in const.GREEN or webexStatus in const.OFF) and officeStatus not in const.OFF:
            logger.debug('Using officeStatus: %s', officeStatus)
            currentStatus = officeStatus
        
        if lastStatus != currentStatus:
            lastStatus = currentStatus

            print()
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Found new status:',currentStatus, end='', flush=True)
            logger.info('Transitioning to %s',currentStatus)
            light.transitionStatus(currentStatus)
        else:
            print('.', end='', flush=True)

        # Sleep for a few seconds    
        time.sleep(5)
except KeyboardInterrupt:
    pass
except BaseException as e:
    logger.warning('Exception during main loop: %s', e)

print()
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Shutdown')
logger.info('Shutdown')
logger.debug('Turning light off')
light.off()
