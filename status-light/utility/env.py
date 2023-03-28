"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Environment Variable Management
"""

# Standard imports
from datetime import datetime, time
import os
import logging

# Project imports
from utility import enum
from utility import util

logger = logging.getLogger(__name__)


class Environment:
    tuya_device: str = ''
    tuya_brightness: int = 128

    # 32 - SOURCES variable default is wrong
    # 32 Recurred; _parseSource expects a string, not a list. Convert the list to a string.
    selected_sources: list[enum.StatusSource] = [
        enum.StatusSource.WEBEX, enum.StatusSource.OFFICE365]

    webex_person_id: str = ''
    webex_bot_id: str = ''

    # 48 - Add Slack Support
    slack_user_id: str = ''
    slack_bot_token: str = ''
    # 66 - Add Slack custom status support
    slack_off_status: list[str] = [
        ':no_entry: Out of Office', ':airplane:', ':palm_tree: Vacationing']
    slack_available_status: list[str] = ['']
    slack_scheduled_status: list[str] = [':spiral_calendar_pad: In a meeting']
    slack_busy_status: list[str] = [':no_entry_sign: Do not Disturb']

    office_app_id: str = ''
    office_app_secret: str = ''
    office_token_store: str = '~'

    # 47 - Add Google support
    # This is the relative path from status-light.py
    google_credential_store: str = './utility/api/calendar/google'
    google_token_store: str = '~'

    # 38 - Working Elsewhere isn't handled
    off_status: list[enum.Status] = [enum.Status.INACTIVE, enum.Status.OUTOFOFFICE,
                                     enum.Status.WORKINGELSEWHERE, enum.Status.UNKNOWN, enum.Status.FREE]
    available_status: list[enum.Status] = [enum.Status.ACTIVE]
    scheduled_status: list[enum.Status] = [
        enum.Status.BUSY, enum.Status.TENTATIVE]
    busy_status: list[enum.Status] = [enum.Status.CALL, enum.Status.DONOTDISTURB,
                                      enum.Status.MEETING, enum.Status.PRESENTING, enum.Status.PENDING]

    available_color: str = enum.Color.GREEN.value
    scheduled_color: str = enum.Color.ORANGE.value
    busy_color: str = enum.Color.RED.value

    # 45 - Add support for active hours
    active_days: list[enum.Weekday] = [enum.Weekday.SUNDAY, enum.Weekday.MONDAY, enum.Weekday.TUESDAY,
                                       enum.Weekday.WEDNESDAY, enum.Weekday.THURSDAY, enum.Weekday.FRIDAY, enum.Weekday.SATURDAY]
    active_hours_start: time = time(hour=0, minute=0, second=0)
    active_hours_end: time = time(hour=23, minute=59, second=59)

    # 22 - Make sleep timeout configurable
    sleep_seconds: int = 5

    # 23 - Make logging level configurable
    log_level: enum.LogLevel = enum.LogLevel.WARNING

    def get_sources(self) -> bool:
        # 32 - SOURCES variable default is wrong
        self.selected_sources = util.parse_enum_list(os.environ.get('SOURCES'),
                                                     enum.StatusSource, 'SOURCES', self.selected_sources)
        return_value = (None is not self.selected_sources)
        # 34 - Better environment variable errors
        # SOURCES is required
        if not return_value:
            logger.warning('SOURCES - at least one source is required!')
        return return_value

    def get_tuya(self) -> bool:
        return_value = True
        # 30: This variable could contain secrets
        self.tuya_device = util.get_env_or_secret('TUYA_DEVICE', '')
        # 34 - Better environment variable errors
        # TUYA_DEVICE is required
        if '' in [self.tuya_device]:
            logger.warning('TUYA_DEVICE is required!')
            return_value = False

        # 41: Replace decorator with utility function
        self.tuya_brightness = util.try_parse_int(os.environ.get('TUYA_BRIGHTNESS', ''),
                                                  self.tuya_brightness)
        # 34 - Better environment variable errors
        # TUYA_BRIGHTNESS should be within the range 32..255
        if self.tuya_brightness < 32 or self.tuya_brightness > 255:
            logger.warning('TUYA_BRIGHTNESS must be between 32 and 255!')
            return_value = False

        return return_value

    def get_webex(self) -> bool:
        # 30: This variable could contain secrets
        self.webex_person_id = util.get_env_or_secret('WEBEX_PERSONID', '')
        # 30: This variable could contain secrets
        self.webex_bot_id = util.get_env_or_secret('WEBEX_BOTID', '')
        return ('' not in [self.webex_person_id, self.webex_bot_id])

    def get_slack(self) -> bool:
        # 30: This variable could contain secrets
        self.slack_user_id = util.get_env_or_secret('SLACK_USER_ID', '')
        # 30: This variable could contain secrets
        self.slack_bot_token = util.get_env_or_secret('SLACK_BOT_TOKEN', '')
        # 66: Support Slack custom statuses
        # NOTE: Since these are all optional, and at least one defaults to '',
        # they should not be checked in the return statement
        self.slack_available_status = util.parse_str_array(os.environ.get('SLACK_AVAILABLE_STATUS', ''),
                                                           self.slack_available_status, casefold=True)
        self.slack_busy_status = util.parse_str_array(os.environ.get('SLACK_BUSY_STATUS', ''),
                                                      self.slack_busy_status, casefold=True)
        self.slack_off_status = util.parse_str_array(os.environ.get('SLACK_OFF_STATUS', ''),
                                                     self.slack_off_status, casefold=True)
        self.slack_scheduled_status = util.parse_str_array(os.environ.get('SLACK_SCHEDULED_STATUS', ''),
                                                           self.slack_scheduled_status, casefold=True)
        return ('' not in [self.slack_user_id, self.slack_bot_token])

    def get_office(self) -> bool:
        # 30: This variable could contain secrets
        self.office_app_id = util.get_env_or_secret('O365_APPID', '')
        # 30: This variable could contain secrets
        self.office_app_secret = util.get_env_or_secret('O365_APPSECRET', '')
        self.office_token_store = os.environ.get(
            'O365_TOKENSTORE', self.office_token_store)
        return ('' not in [self.office_app_id, self.office_app_secret, self.office_token_store])

    # 47: Add Google support
    def get_google(self) -> bool:
        self.google_credential_store = os.environ.get('GOOGLE_CREDENTIALSTORE',
                                                      self.google_credential_store)
        self.google_token_store = os.environ.get('GOOGLE_TOKENSTORE',
                                                 self.google_token_store)
        return ('' not in [self.google_credential_store, self.google_token_store])

    def get_colors(self) -> bool:
        self.available_color = util.parse_color(os.environ.get('AVAILABLE_COLOR', ''),
                                                self.available_color)
        self.scheduled_color = util.parse_color(os.environ.get('SCHEDULED_COLOR', ''),
                                                self.scheduled_color)
        self.busy_color = util.parse_color(os.environ.get('BUSY_COLOR', ''),
                                           self.busy_color)
        return ('' not in [self.available_color, self.scheduled_color, self.busy_color])

    def get_status(self) -> bool:
        self.off_status = util.parse_enum_list(os.environ.get('OFF_STATUS', ''),
                                               enum.Status, 'OFF_STATUS', self.off_status)
        self.available_status = util.parse_enum_list(os.environ.get('AVAILABLE_STATUS', ''),
                                                     enum.Status, 'AVAILABLE_STATUS', self.available_status)
        self.busy_status = util.parse_enum_list(os.environ.get('BUSY_STATUS', ''),
                                                enum.Status, 'BUSY_STATUS', self.busy_status)
        self.scheduled_status = util.parse_enum_list(os.environ.get('SCHEDULED_STATUS', ''),
                                                     enum.Status, 'SCHEDULED_STATUS', self.scheduled_status)
        return ('' not in [self.off_status, self.available_status,
                           self.busy_status, self.scheduled_status])

    # 45 - Allow user to specify active hours
    def get_active_time(self) -> bool:
        self.active_days = util.parse_enum_list(os.environ.get('ACTIVE_DAYS', ''),
                                                enum.Weekday, 'ACTIVE_DAYS', self.active_days)
        self.active_hours_start = util.try_parse_datetime(
            os.environ.get('ACTIVE_HOURS_START', ''),
            datetime.combine(datetime.today(), self.active_hours_start)).time()
        self.active_hours_end = util.try_parse_datetime(
            os.environ.get('ACTIVE_HOURS_END', ''),
            datetime.combine(datetime.today(), self.active_hours_end)).time()

        return ('' not in [self.active_days, self.active_hours_start,
                           self.active_hours_end])

    def get_sleep(self) -> bool:
        # 41: Replace decorator with utility function
        self.sleep_seconds = util.try_parse_int(os.environ.get('SLEEP_SECONDS', ''),
                                                self.sleep_seconds)
        return self.sleep_seconds >= 5 and self.sleep_seconds <= 60

    def get_log_level(self) -> bool:
        self.log_level = util.parse_enum(os.environ.get('LOGLEVEL', ''),
                                         enum.LogLevel, 'LOGLEVEL', self.log_level)
        return self.log_level != ''
