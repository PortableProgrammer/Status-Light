"""Status-Light
(c) 2020-2023 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Main Application Entry Point
"""

# Standard imports
import sys
import signal
import time
import logging
from datetime import datetime

# Project imports
from sources.collaboration import webex
# 48 - Add Slack support
from sources.collaboration import slack
from sources.calendar import office365
# 47 - Add Google support
from sources.calendar import google
from targets import tuya
from utility import env
from utility import enum
from utility import util

currentStatus: enum.Status = enum.Status.UNKNOWN
lastStatus: enum.Status = currentStatus
shouldContinue: bool = True

# 67 - Include function name in the basic logger format
logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.WARNING)
logger: logging.Logger = logging.getLogger(__name__)

logger.info('Startup')
print(datetime.now().strftime(
    '[%Y-%m-%d %H:%M:%S]'), 'Startup')  # type: ignore

# Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
# At the moment, we'll treat them all the same and exit cleanly
# Since these are OS-level calls, we'll just ignore the argument issues

def receive_signal(signal_number, frame):
    """Signals the endless while loop to exit, allowing a clean shutdown."""
    # 74: Convert integer to signal name
    # Don't allow this to fail, just continue on
    signal_name = 'UNKNOWN'
    try:
        signal_name = signal.Signals(signal_number).name
    except ValueError:
        logger.warning(
            'Exception encountered converting %s to signal.Signals: %s', signal_number, ex)
    logger.warning('Signal received: %s', signal_name)
    # TODO: Find a better way to handle this
    global shouldContinue
    shouldContinue = False


signals: list[signal.Signals] = [signal.SIGHUP,
                                 signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]
for sig in signals:
    signal.signal(sig, receive_signal)

# Validate environment variables in a structured way
localEnv = env.Environment()
if False in [localEnv.get_sources(), localEnv.get_tuya(), localEnv.get_colors(),
             localEnv.get_status(), localEnv.get_active_time(), localEnv.get_sleep(),
             localEnv.get_log_level()]:

    # We failed to gather some environment variables
    logger.warning('Failed to find all environment variables!')
    sys.exit(1)

# 23 - Make logging level configurable
logger.info('Setting log level to %s', localEnv.log_level.name)
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'Setting log level to',
      localEnv.log_level.name)
logger.setLevel(localEnv.log_level.value)

# Depending on the selected sources, get the environment
webex_api: webex.WebexAPI = webex.WebexAPI()
if enum.StatusSource.WEBEX in localEnv.selected_sources:
    if localEnv.get_webex():
        logger.info('Requested Webex')
        webex_api.botID = localEnv.webex_bot_id
    else:
        logger.warning(
            'Requested Webex, but could not find all environment variables!')
        sys.exit(1)

slack_api: slack.SlackAPI = slack.SlackAPI()
if enum.StatusSource.SLACK in localEnv.selected_sources:
    if localEnv.get_slack():
        logger.info('Requested Slack')
        slack_api.user_id = localEnv.slack_user_id
        slack_api.bot_token = localEnv.slack_bot_token
        # 66 - Support Slack custom statuses
        slack_api.custom_available_status = localEnv.slack_available_status
        slack_api.custom_available_status_map = localEnv.available_status[0]
        slack_api.custom_busy_status = localEnv.slack_busy_status
        slack_api.custom_busy_status_map = localEnv.busy_status[0]
        slack_api.custom_off_status = localEnv.slack_off_status
        slack_api.custom_off_status_map = localEnv.off_status[0]
        slack_api.custom_scheduled_status = localEnv.slack_scheduled_status
        slack_api.custom_scheduled_status_map = localEnv.scheduled_status[0]
    else:
        logger.warning(
            'Requested Slack, but could not find all environment variables!')
        sys.exit(1)

office_api: office365.OfficeAPI = office365.OfficeAPI()
if enum.StatusSource.OFFICE365 in localEnv.selected_sources:
    if localEnv.get_office():
        logger.info('Requested Office 365')
        office_api.appID = localEnv.office_app_id
        office_api.appSecret = localEnv.office_app_secret
        office_api.tokenStore = localEnv.office_token_store
        office_api.authenticate()
    else:
        logger.warning(
            'Requested Office 365, but could not find all environment variables!')
        sys.exit(1)

# 47 - Add Google support
google_api: google.GoogleCalendarAPI = google.GoogleCalendarAPI()
if enum.StatusSource.GOOGLE in localEnv.selected_sources:
    if localEnv.get_google():
        logger.info('Requested Google')
        google_api.credentialStore = localEnv.google_credential_store
        google_api.tokenStore = localEnv.google_token_store
    else:
        logger.warning(
            'Requested Google, but could not find all environment variables!')
        sys.exit(1)

# Tuya
light = tuya.TuyaLight()
# TUYA_DEVICE is a JSON string, and needs to be converted to an actual JSON object
light.device = eval(localEnv.tuya_device)
logger.debug('Retrieved TUYA_DEVICE variable: %s', light.device)
# TODO: Connect to the device and ensure it's available
# light.getCurrentStatus()

outside_hours = False
while shouldContinue:
    try:
        # Decide if we need to poll at this time
        if util.is_active_hours(localEnv.active_days, localEnv.active_hours_start,
                                localEnv.active_hours_end):

            outside_hours = False

            webexStatus = enum.Status.UNKNOWN
            slackStatus = enum.Status.UNKNOWN
            officeStatus = enum.Status.UNKNOWN
            googleStatus = enum.Status.UNKNOWN

            logger_format = " {}: {} |"
            logger_string = ""

            # Webex Status
            if enum.StatusSource.WEBEX in localEnv.selected_sources:
                webexStatus = webex_api.get_person_status(
                    localEnv.webex_person_id)
                logger_string += logger_format.format(enum.StatusSource.WEBEX.name.capitalize(),
                                                      webexStatus.name.lower())

            # Slack Status
            if enum.StatusSource.SLACK in localEnv.selected_sources:
                slackStatus = slack_api.get_user_presence()
                logger_string += logger_format.format(enum.StatusSource.SLACK.name.capitalize(),
                                                      slackStatus.name.lower())

            # O365 Status (based on calendar)
            if enum.StatusSource.OFFICE365 in localEnv.selected_sources:
                officeStatus = office_api.get_current_status()
                logger_string += logger_format.format(enum.StatusSource.OFFICE365.name.capitalize(),
                                                      officeStatus.name.lower())

            # Google Status (based on calendar)
            if enum.StatusSource.GOOGLE in localEnv.selected_sources:
                googleStatus = google_api.get_current_status()
                logger_string += logger_format.format(enum.StatusSource.GOOGLE.name.capitalize(),
                                                      googleStatus.name.lower())

            # 74: Log enums as names, not values
            # logger.debug('Webex: %s | Slack: %s | Office: %s | Google: %s',
            #    webexStatus.name.lower(), slackStatus.name.lower(), officeStatus.name.lower(), googleStatus.name.lower())

            logger.info(logger_string.lstrip().rstrip(' |'))

            # TODO: Now that we have more than one calendar-based status source,
            # build a real precedence module for these
            # Compare statii and pick a winner
            # Collaboration status always wins except in specific scenarios
            # Webex currently takes precendence over Slack
            currentStatus = webexStatus
            if webexStatus == enum.Status.UNKNOWN or webexStatus in localEnv.off_status:
                # 74: Log enums as names, not values
                logger.debug('Using slackStatus: %s', slackStatus.name.lower())
                # Fall through to Slack
                currentStatus = slackStatus

            if (currentStatus in localEnv.available_status or
                currentStatus in localEnv.off_status) \
                and (officeStatus not in localEnv.off_status
                     or googleStatus not in localEnv.off_status):

                logger.debug('Using calendar-based status')
                # Office should take precedence over Google for now
                # 74: Log enums as names, not values
                if officeStatus != enum.Status.UNKNOWN:
                    logger.debug('Using officeStatus: %s',
                                 officeStatus.name.lower())
                    currentStatus = officeStatus
                else:
                    logger.debug('Using googleStatus: %s',
                                 googleStatus.name.lower())
                    currentStatus = googleStatus

            if lastStatus != currentStatus:
                lastStatus = currentStatus

                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
                      'Found new status:', currentStatus.name.lower(), flush=True)
                # 74: Log enums as names, not values
                logger.info('Transitioning to %s', currentStatus.name.lower())
                light.transition_status(currentStatus, localEnv)

        else:
            if outside_hours:
                logger.debug('Already transitioned to off, doing nothing')
            else:
                logger.info('Outside of active hours, transitioning to off')
                light.turn_off()
            outside_hours = True

        # Sleep for a few seconds
        time.sleep(localEnv.sleep_seconds)
    except (SystemExit, KeyboardInterrupt) as ex:
        logger.info('%s received; shutting down...', ex.__class__.__name__)
        shouldContinue = False
    except BaseException as ex:
        logger.warning('Exception during main loop: %s', ex)
        logger.debug(ex)

print()
print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'Shutdown')
logger.info('Shutdown')
logger.debug('Turning light off')
light.turn_off()
