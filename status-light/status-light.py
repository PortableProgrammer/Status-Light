# https://github.com/portableprogrammer/Status-Light/

# Module imports
import sys
import signal
#import os
import time
import logging
from datetime import datetime

# Project imports
from sources.collaboration import webex
from sources.calendar import office365
# 47 - Add Google support
from sources.calendar import google
from targets import tuya
from utility import env
from utility import const

currentStatus = const.Status.unknown
lastStatus = currentStatus

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.WARNING)
logger = logging.getLogger(__name__)

logger.info('Startup')
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Startup')

# Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
# At the moment, we'll treat them all (but SIGTERM) the same and exit
shouldContinue = True
def receiveSignal(signalNumber, frame):
    logger.warning('\nSignal received: %s', signalNumber)
    # TODO: Make better choices here, this is really a hack
    global shouldContinue
    shouldContinue = False
    return

# SIGTERM should be handled special
def receiveTerminate(signalNumber, frame):
    logger.warning('\nSIGTERM received, terminating immediately')
    sys.exit(0)
    
signals = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT]
for sig in signals:
    signal.signal(sig, receiveSignal)
signal.signal(signal.SIGTERM, receiveTerminate)

# Validate environment variables in a structured way
localEnv = env.Environment()
if False in [localEnv.getSources(), localEnv.getTuya(), localEnv.getColors(), localEnv.getStatus(), localEnv.getSleep(), localEnv.getLogLevel()]:
    # We failed to gather some environment variables
    logger.warning('Failed to find all environment variables!')
    sys.exit(1)

# 23 - Make logging level configurable
logger.info('Setting log level to %s', localEnv.logLevel)
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Setting log level to', localEnv.logLevel)
logger.setLevel(localEnv.logLevel)

# Depending on the selected sources, get the environment
webexAPI = None
if const.StatusSource.webex in localEnv.selectedSources:
    if localEnv.getWebex():
        logger.info('Requested Webex')
        webexAPI = webex.WebexAPI()
        webexAPI.botID = localEnv.webexBotID
    else:
        logger.warning('Requested Webex, but could not find all environment variables!')
        sys.exit(1)

officeAPI = None
if const.StatusSource.office365 in localEnv.selectedSources:
    if localEnv.getOffice():
        logger.info('Requested Office 365')
        officeAPI = office365.OfficeAPI()
        officeAPI.appID = localEnv.officeAppID
        officeAPI.appSecret = localEnv.officeAppSecret
        officeAPI.tokenStore = localEnv.officeTokenStore
        officeAPI.authenticate()
    else:
        logger.warning('Requested Office 365, but could not find all environment variables!')
        sys.exit(1)

# 47 - Add Google support
googleAPI = None
if const.StatusSource.google in localEnv.selectedSources:
    if localEnv.getGoogle():
        logger.info('Requested Google')
        googleAPI = google.GoogleAPI()
        googleAPI.credentialStore = localEnv.googleCredentialStore
        googleAPI.tokenStore = localEnv.googleTokenStore
    else:
        logger.warning('Requested Google, but could not find all environment variables!')
        sys.exit(1)

# Tuya
light = tuya.TuyaLight()
# TUYA_DEVICE is a JSON string, and needs to be converted to an actual JSON object
light.device = eval(localEnv.tuyaDevice)
logger.debug('Retrieved TUYA_DEVICE variable: %s', light.device)
# TODO: Connect to the device and ensure it's available
#light.getCurrentStatus()

while shouldContinue:
    try:
        webexStatus = const.Status.unknown
        officeStatus = const.Status.unknown
        googleStatus = const.Status.unknown

        # Webex Status
        if const.StatusSource.webex in localEnv.selectedSources:
            webexStatus = webexAPI.getPersonStatus(localEnv.webexPersonID)

        # O365 Status (based on calendar)
        if const.StatusSource.office365 in localEnv.selectedSources:
            officeStatus = officeAPI.getCurrentStatus()

        # Google Status (based on calendar)
        if const.StatusSource.google in localEnv.selectedSources:
            googleStatus = googleAPI.getCurrentStatus()
        
        # TODO: Now that we have more than one calendar-based status source, build a real precedence module for these
        # Compare statii and pick a winner
        logger.debug('Webex: %s | Office: %s | Google: %s', webexStatus, officeStatus, googleStatus)
        # Webex status always wins except in specific scenarios
        currentStatus = webexStatus
        if (webexStatus in localEnv.availableStatus or webexStatus in localEnv.offStatus) and (officeStatus not in localEnv.offStatus or googleStatus not in localEnv.offStatus):
            logger.debug('Using calendar-based status')
            # Office should take precedence over Google for now
            if (officeStatus != const.Status.unknown):
                logger.debug('Using officeStatus: %s', officeStatus)
                currentStatus = officeStatus
            else:
                logger.debug('Using googleStatus: %s', googleStatus)
                currentStatus = googleStatus
        
        if lastStatus != currentStatus:
            lastStatus = currentStatus

            print()
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Found new status:',currentStatus, end='', flush=True)
            logger.info('Transitioning to %s',currentStatus)
            light.transitionStatus(currentStatus, localEnv)
        else:
            print('.', end='', flush=True)

        # Sleep for a few seconds    
        time.sleep(localEnv.sleepSeconds)
    except (SystemExit, KeyboardInterrupt) as e:
        logger.info('%s received; shutting down...', e.__class__.__name__)
        shouldContinue = False
    except BaseException as e:
        logger.warning('Exception during main loop: %s', e)
        logger.debug(e)

print()
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Shutdown')
logger.info('Shutdown')
logger.debug('Turning light off')
light.off()
