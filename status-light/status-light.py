"""Status-Light
(c) 2020-2023 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Main Application Entry Point
"""
# PyLint complains about `status-light`, but it's effectively set in stone now.
# This will also disable this check for the whole module file, but we've already
#   fixed everything else.
# pylint: disable=invalid-name

# Standard imports
import logging
import signal
import sys
import time

# Project imports
# 47 - Add Google support
from sources.calendar import google, ics, office365
# 48 - Add Slack support
from sources.collaboration import slack, webex
from targets import tuya
from utility import enum, env, util


class StatusLight:
    """Provides a structured entry point for the Status-Light application"""
    # Instance Logger
    logger: logging.Logger = logging.getLogger('status-light')

    # Instance Properties
    local_env = env.Environment()
    current_status: enum.Status = enum.Status.UNKNOWN
    last_status: enum.Status = current_status
    should_continue: bool = True

    # Source Properties
    webex_api: webex.WebexAPI = webex.WebexAPI()
    slack_api: slack.SlackAPI = slack.SlackAPI()
    office_api: office365.OfficeAPI = office365.OfficeAPI()
    google_api: google.GoogleCalendarAPI = google.GoogleCalendarAPI()
    ics_api: ics.Ics = ics.Ics()

    # Target Properties
    light: tuya.TuyaLight = tuya.TuyaLight()

    def init(self):
        """Initializes all class and environment variables."""
        # Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
        signals: list[signal.Signals] = [signal.SIGHUP,
                                         signal.SIGINT,
                                         signal.SIGQUIT,
                                         signal.SIGTERM]
        for sig in signals:
            signal.signal(sig, receive_signal)

        # Validate environment variables in a structured way
        if False in [self.local_env.get_sources(),
                     self.local_env.get_tuya(),
                     self.local_env.get_colors(),
                     self.local_env.get_status(),
                     self.local_env.get_active_time(),
                     self.local_env.get_lookahead(),
                     self.local_env.get_sleep(),
                     self.local_env.get_log_level()]:

            # We failed to gather some environment variables
            self.logger.error('Failed to find all environment variables!')
            sys.exit(1)

        # 23 - Make logging level configurable
        self.logger.info('Setting log level to %s', self.local_env.log_level.name)
        # Reset the root logger config to our epxected logging level
        logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]', level=self.local_env.log_level.value, force=True)
        self.logger.setLevel(self.local_env.log_level.value)

        # Depending on the selected sources, get the environment
        if enum.StatusSource.WEBEX in self.local_env.selected_sources:
            if self.local_env.get_webex():
                self.logger.info('Requested Webex')
                self.webex_api.bot_id = self.local_env.webex_bot_id
                self.webex_api.person_id = self.local_env.webex_person_id
            else:
                self.logger.error(
                    'Requested Webex, but could not find all environment variables!')
                sys.exit(1)

        if enum.StatusSource.SLACK in self.local_env.selected_sources:
            if self.local_env.get_slack():
                self.logger.info('Requested Slack')
                self.slack_api.user_id = self.local_env.slack_user_id
                self.slack_api.bot_token = self.local_env.slack_bot_token
                # 66 - Support Slack custom statuses
                self.slack_api.custom_available_status = self.local_env.slack_available_status
                self.slack_api.custom_available_status_map = self.local_env.available_status[
                    0]
                self.slack_api.custom_busy_status = self.local_env.slack_busy_status
                self.slack_api.custom_busy_status_map = self.local_env.busy_status[0]
                self.slack_api.custom_off_status = self.local_env.slack_off_status
                self.slack_api.custom_off_status_map = self.local_env.off_status[0]
                self.slack_api.custom_scheduled_status = self.local_env.slack_scheduled_status
                self.slack_api.custom_scheduled_status_map = self.local_env.scheduled_status[
                    0]
            else:
                self.logger.error(
                    'Requested Slack, but could not find all environment variables!')
                sys.exit(1)

        if enum.StatusSource.OFFICE365 in self.local_env.selected_sources:
            if self.local_env.get_office():
                self.logger.info('Requested Office 365')
                self.office_api.appID = self.local_env.office_app_id
                self.office_api.appSecret = self.local_env.office_app_secret
                self.office_api.tokenStore = self.local_env.office_token_store
                # 81 - Make calendar lookahead configurable
                self.office_api.lookahead = self.local_env.calendar_lookahead
                self.office_api.authenticate()
            else:
                self.logger.error(
                    'Requested Office 365, but could not find all environment variables!')
                sys.exit(1)

        # 47 - Add Google support
        if enum.StatusSource.GOOGLE in self.local_env.selected_sources:
            if self.local_env.get_google():
                self.logger.info('Requested Google')
                self.google_api.credentialStore = self.local_env.google_credential_store
                self.google_api.tokenStore = self.local_env.google_token_store
                # 81 - Make calendar lookahead configurable
                self.google_api.lookahead = self.local_env.calendar_lookahead
            else:
                self.logger.error(
                    'Requested Google, but could not find all environment variables!')
                sys.exit(1)

        # ICS Calendar support
        if enum.StatusSource.ICS in self.local_env.selected_sources:
            if self.local_env.get_ics():
                self.logger.info('Requested ICS')
                self.ics_api.url = self.local_env.ics_url
                self.ics_api.cacheStore = self.local_env.ics_cache_store
                self.ics_api.cacheLifetime = self.local_env.ics_cache_lifetime
                # 81 - Make calendar lookahead configurable
                self.ics_api.lookahead = self.local_env.calendar_lookahead
            else:
                self.logger.error(
                    'Requested ICS, but could not find all environment variables!')
                sys.exit(1)

        # Tuya
        self.light.device = self.local_env.tuya_device
        self.logger.debug('Retrieved TUYA_DEVICE variable: %s', self.light.device)
        tuya_status = self.light.get_status()
        self.logger.debug('Found initial Tuya status: %s', tuya_status)
        if not tuya_status:
            self.logger.error(
                'Could not connect to Tuya device!')
            sys.exit(1)

    def run(self):
        """Runs the main loop of the application"""
        # We only want to perform the "outside of active hours" activity once
        already_handled_inactive_hours = False
        # Init to True so we don't panic the first time
        last_transition_result = True
        while self.should_continue:
            try:
                # Decide if we need to poll at this time
                if util.is_active_hours(self.local_env.active_days,
                                        self.local_env.active_hours_start,
                                        self.local_env.active_hours_end):

                    self.logger.debug('Within Active Hours, polling')

                    # Reset the "outside of active hours" handler
                    already_handled_inactive_hours = False

                    webex_status = enum.Status.UNKNOWN
                    slack_status = enum.Status.UNKNOWN
                    office_status = enum.Status.UNKNOWN
                    google_status = enum.Status.UNKNOWN
                    ics_status = enum.Status.UNKNOWN

                    logger_format = " {}: {} |"
                    logger_string = ""

                    # Webex Status
                    if enum.StatusSource.WEBEX in self.local_env.selected_sources:
                        webex_status = self.webex_api.get_person_status()
                        logger_string += \
                            logger_format.format(enum.StatusSource.WEBEX.name.capitalize(),
                                                 webex_status.name.lower())

                    # Slack Status
                    if enum.StatusSource.SLACK in self.local_env.selected_sources:
                        slack_status = self.slack_api.get_user_presence()
                        logger_string += \
                            logger_format.format(enum.StatusSource.SLACK.name.capitalize(),
                                                 slack_status.name.lower())

                    # O365 Status (based on calendar)
                    if enum.StatusSource.OFFICE365 in self.local_env.selected_sources:
                        office_status = self.office_api.get_current_status()
                        logger_string += \
                            logger_format.format(enum.StatusSource.OFFICE365.name.capitalize(),
                                                 office_status.name.lower())

                    # Google Status (based on calendar)
                    if enum.StatusSource.GOOGLE in self.local_env.selected_sources:
                        google_status = self.google_api.get_current_status()
                        logger_string += \
                            logger_format.format(enum.StatusSource.GOOGLE.name.capitalize(),
                                                 google_status.name.lower())

                    # ICS Status (based on calendar)
                    if enum.StatusSource.ICS in self.local_env.selected_sources:
                        ics_status = self.ics_api.get_current_status()
                        logger_string += \
                            logger_format.format(enum.StatusSource.ICS.name.capitalize(),
                                                 ics_status.name.lower())

                    # 74: Log enums as names, not values
                    self.logger.debug(logger_string.lstrip().rstrip(' |'))

                    # TODO: Now that we have more than one calendar-based status source,
                    # build a real precedence module for these
                    # Compare statii and pick a winner
                    # Collaboration status always wins except in specific scenarios
                    # Webex currently takes precendence over Slack
                    self.current_status = webex_status
                    if (webex_status == enum.Status.UNKNOWN or
                            webex_status in self.local_env.off_status):
                        # 74: Log enums as names, not values
                        self.logger.debug('Using slack_status: %s',
                                     slack_status.name.lower())
                        # Fall through to Slack
                        self.current_status = slack_status

                    if (self.current_status in self.local_env.available_status or
                        self.current_status in self.local_env.off_status) \
                        and (office_status not in self.local_env.off_status
                             or google_status not in self.local_env.off_status
                             or ics_status not in self.local_env.off_status):

                        self.logger.debug('Using calendar-based status')
                        # Office should take precedence over Google, Google over ICS
                        # 74: Log enums as names, not values
                        if office_status != enum.Status.UNKNOWN:
                            self.logger.debug('Using office_status: %s',
                                         office_status.name.lower())
                            self.current_status = office_status
                        elif google_status != enum.Status.UNKNOWN:
                            self.logger.debug('Using google_status: %s',
                                         google_status.name.lower())
                            self.current_status = google_status
                        else:
                            self.logger.debug('Using ics_status: %s',
                                         ics_status.name.lower())
                            self.current_status = ics_status

                    status_changed = False
                    if self.last_status != self.current_status:
                        self.last_status = self.current_status
                        status_changed = True

                    if status_changed:
                        self.logger.info('Found new status: %s',
                                    self.current_status.name.lower())

                    if not last_transition_result:
                        self.logger.warning(
                            'Last attempt to set status failed. Retrying.')

                    # If status changed this loop
                    # 40: or the last transition failed,
                    if status_changed or not last_transition_result:
                        # 74: Log enums as names, not values
                        self.logger.info('Transitioning to %s',
                                    self.current_status.name.lower())
                        last_transition_result = self._transition_status()

                else:
                    self.logger.debug('Outside Active Hours, pausing')

                    if not already_handled_inactive_hours:
                        self.logger.info(
                            'Outside of active hours, transitioning to off')
                        last_transition_result = self.light.off()
                        self.last_status = enum.Status.UNKNOWN
                        already_handled_inactive_hours = True

                    # 40: If the last transition failed, try again
                    if not last_transition_result:
                        last_transition_result = self.light.off()

                # Sleep for a few seconds
                time.sleep(self.local_env.sleep_seconds)
            except (SystemExit, KeyboardInterrupt) as ex:
                self.logger.info('%s received; shutting down...',
                            ex.__class__.__name__)
                self.should_continue = False
            except Exception as ex:  # pylint: disable=broad-except
                self.logger.warning('Exception during main loop: %s', ex)
                self.logger.exception(ex)

        self.logger.debug('Turning light off')
        self.light.off()

    def _transition_status(self) -> bool:
        """Internal Helper Method to determine the correct color for the light
        and transition to it."""
        # 43: Coalesce the statuses and only execute setState once.
        # This will still allow a single status to be in more than one list,
        # but will not cause the light to rapidly switch between states.
        color = None
        return_value = False

        if self.current_status in self.local_env.available_status:
            color = self.local_env.available_color

        if self.current_status in self.local_env.scheduled_status:
            color = self.local_env.scheduled_color

        if self.current_status in self.local_env.busy_status:
            color = self.local_env.busy_color

        if color is not None:
            return_value = self.light.set_status(
                enum.TuyaMode.COLOR, color, self.local_env.tuya_brightness)
        # OffStatus has the lowest priority, so only check it if none of the others are valid
        elif self.current_status in self.local_env.off_status:
            return_value = self.light.off()
        # In the case that we made it here without a valid state,
        # just turn the light off and warn about it
        # 74: Log enums as names, not values
        else:
            self.logger.warning('Called with an invalid status: %s',
                           self.current_status.name.lower())
            return_value = self.light.off()

        return return_value


# Globals
status_light: StatusLight = StatusLight()

# 67 - Include function name in the basic logger format
# Default to INFO level until we load the environment
logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]', level=logging.INFO)
global_logger: logging.Logger = logging.getLogger('status-light')


def receive_signal(signal_number, frame):  # pylint: disable=unused-argument
    """Signals the endless while loop to exit, allowing a clean shutdown."""
    # Register for SIGHUP, SIGINT, SIGQUIT, SIGTERM
    # At the moment, we'll treat them all the same and exit cleanly
    # Since these are OS-level calls, we'll just ignore the argument issues

    # 74: Convert integer to signal name
    # Don't allow this to fail, just continue on
    signal_name = 'UNKNOWN'
    try:
        signal_name = signal.Signals(signal_number).name
    except ValueError as value_ex:
        global_logger.warning(
            'Exception encountered converting %s to signal.Signals: %s', signal_number, value_ex)
    global_logger.warning('Signal received: %s', signal_name)
    status_light.should_continue = False


# Main Methods


def main():
    """Provides the entry point for the application"""
    global_logger.info('Startup')
    status_light.init()
    status_light.run()
    global_logger.info('Shutdown')


if __name__ == '__main__':
    main()
