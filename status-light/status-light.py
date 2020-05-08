# https://github.com/portableprogrammer/Status-Light/

# Module imports
import sys
import signal
import os
import time
import logging
from datetime import datetime

# Project imports
import webex
import office365
import tuya
import env
import const

currentStatus = const.Status.unknown
lastStatus = currentStatus

# TODO: Dynamic logging level
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.WARNING)
logger = logging.getLogger(__name__)

logger.info('Startup')
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Startup')

# Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
# At the moment, we'll treat them all (but SIGTERM) the same and exit
shouldContinue = True
def receiveSignal(signalNumber, frame):
    logger.warning('Signal received: %s', signalNumber)
    # TODO: Make better choices here, this is really a hack
    global shouldContinue
    shouldContinue = False
    return

# SIGTERM should be handled special
def receiveTerminate(signalNumber, frame):
    logger.warning('SIGTERM received, terminating immediately')
    sys.exit(0)
    
signals = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT]
for sig in signals:
    signal.signal(sig, receiveSignal)
signal.signal(signal.SIGTERM, receiveTerminate)

# TODO: Gather and validate environment variables in a structured way
localEnv = env.Environment()
if False in [localEnv.getTuya(), localEnv.getWebex(), localEnv.getOffice()]:
    # We failed to gather some environment variables
    logger.warning('Failed to find all environment variables!')
    sys.exit(1)

# Tuya
light = tuya.TuyaLight()
light.device = eval(localEnv.tuyaDevice)
logger.debug('Retrieved TUYA_DEVICE variable: %s', light.device)
# TODO: Connect to the device and ensure it's available
#light.getCurrentStatus()

# Webex
webexAPI = webex.WebexAPI()
webexAPI.botID = localEnv.webexBotID

# Office365 
officeAPI = office365.OfficeAPI()
officeAPI.appID = localEnv.officeAppID
officeAPI.appSecret = localEnv.officeAppSecret
officeAPI.tokenStore = localEnv.officeTokenStore
officeAPI.authenticate()

while shouldContinue:
    try:
        # Webex Status
        webexStatus = webexAPI.getPersonStatus(localEnv.webexPersonID)

        # O365 Status (based on calendar)
        officeStatus = officeAPI.getCurrentStatus()
        
        # Compare statii and pick a winner
        logger.debug('Webex: %s | Office: %s', webexStatus, officeStatus)
        # Webex status always wins except in specific scenarios
        currentStatus = webexStatus
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
    except BaseException as e:
        logger.warning('Exception during main loop: %s', e)

print()
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Shutdown')
logger.info('Shutdown')
logger.debug('Turning light off')
light.off()
