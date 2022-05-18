# https://github.com/portableprogrammer/Status-Light/

# Standard imports
import sys
import signal
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
shouldContinue = True

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.WARNING)
logger = logging.getLogger(__name__)

logger.info('Startup')
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Startup')

# Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
# At the moment, we'll treat them all (but SIGTERM) the same and exit
# Since these are OS-level calls, we'll just ignore the argument issues
# pylint: disable=unused-argument
def receive_signal(signal_number, frame):
    logger.warning('\nSignal received: %s', signal_number)
    # Since this controls the infinite while loop, it should stay
    # pylint: disable=global-statement
    global shouldContinue
    shouldContinue = False
    return

# SIGTERM should be handled special
# Since these are OS-level calls, we'll just ignore the argument issues
# pylint: disable=unused-argument
def receive_terminate(signal_number, frame):
    logger.warning('\nSIGTERM received, terminating immediately')
    sys.exit(0)

signals = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT]
for sig in signals:
    signal.signal(sig, receive_signal)
signal.signal(signal.SIGTERM, receive_terminate)

# Validate environment variables in a structured way
localEnv = env.Environment()
if False in [localEnv.get_sources(), localEnv.get_tuya(), localEnv.get_colors(),
    localEnv.get_status(), localEnv.get_sleep(), localEnv.get_log_level()]:

    # We failed to gather some environment variables
    logger.warning('Failed to find all environment variables!')
    sys.exit(1)

# 23 - Make logging level configurable
logger.info('Setting log level to %s', localEnv.log_level)
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),'Setting log level to', localEnv.log_level)
logger.setLevel(localEnv.log_level)

# Depending on the selected sources, get the environment
webex_api = None
if const.StatusSource.webex in localEnv.selected_sources:
    if localEnv.get_webex():
        logger.info('Requested Webex')
        webex_api = webex.WebexAPI()
        webex_api.botID = localEnv.webex_bot_id
    else:
        logger.warning('Requested Webex, but could not find all environment variables!')
        sys.exit(1)

office_api = None
if const.StatusSource.office365 in localEnv.selected_sources:
    if localEnv.get_office():
        logger.info('Requested Office 365')
        office_api = office365.OfficeAPI()
        office_api.appID = localEnv.office_app_id
        office_api.appSecret = localEnv.office_app_secret
        office_api.tokenStore = localEnv.office_token_store
        office_api.authenticate()
    else:
        logger.warning('Requested Office 365, but could not find all environment variables!')
        sys.exit(1)

# 47 - Add Google support
google_api = None
if const.StatusSource.google in localEnv.selected_sources:
    if localEnv.get_google():
        logger.info('Requested Google')
        google_api = google.GoogleCalendarAPI()
        google_api.credentialStore = localEnv.google_credential_store
        google_api.tokenStore = localEnv.google_token_store
    else:
        logger.warning('Requested Google, but could not find all environment variables!')
        sys.exit(1)

# Tuya
light = tuya.TuyaLight()
# TUYA_DEVICE is a JSON string, and needs to be converted to an actual JSON object
# pylint: disable=eval-used
light.device = eval(localEnv.tuya_device)
logger.debug('Retrieved TUYA_DEVICE variable: %s', light.device)
# TODO: Connect to the device and ensure it's available
#light.getCurrentStatus()

while shouldContinue:
    try:
        webexStatus = const.Status.unknown
        officeStatus = const.Status.unknown
        googleStatus = const.Status.unknown

        # Webex Status
        if const.StatusSource.webex in localEnv.selected_sources:
            webexStatus = webex_api.get_person_status(localEnv.webex_person_id)

        # O365 Status (based on calendar)
        if const.StatusSource.office365 in localEnv.selected_sources:
            officeStatus = office_api.get_current_status()

        # Google Status (based on calendar)
        if const.StatusSource.google in localEnv.selected_sources:
            googleStatus = google_api.get_current_status()

        # TODO: Now that we have more than one calendar-based status source,
        # build a real precedence module for these
        # Compare statii and pick a winner
        logger.debug('Webex: %s | Office: %s | Google: %s', webexStatus, officeStatus, googleStatus)
        # Webex status always wins except in specific scenarios
        currentStatus = webexStatus
        if (webexStatus in localEnv.available_status or webexStatus in localEnv.off_status) \
            and (officeStatus not in localEnv.off_status or googleStatus not in localEnv.off_status):

            logger.debug('Using calendar-based status')
            # Office should take precedence over Google for now
            if officeStatus != const.Status.unknown:
                logger.debug('Using officeStatus: %s', officeStatus)
                currentStatus = officeStatus
            else:
                logger.debug('Using googleStatus: %s', googleStatus)
                currentStatus = googleStatus

        if lastStatus != currentStatus:
            lastStatus = currentStatus

            print()
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
                'Found new status:',currentStatus, end='', flush=True)
            logger.info('Transitioning to %s',currentStatus)
            light.transition_status(currentStatus, localEnv)
        else:
            print('.', end='', flush=True)

        # Sleep for a few seconds
        time.sleep(localEnv.sleep_seconds)
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
light.turn_off()
