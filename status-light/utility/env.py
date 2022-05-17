# Standard imports
import os
import re
import logging

# Project imports
from utility import const
from utility import util

logger = logging.getLogger(__name__)

class Environment:
    tuya_device = None
    tuya_brightness = 128

    #32 - SOURCES variable default is wrong
    #32 Recurred; _parseSource expects a string, not a list. Convert the list to a string.
    selected_sources = 'Webex,Office365'

    webex_person_id = None
    webex_bot_id = None

    office_app_id = None
    office_app_secret = None
    office_token_store = '~'

    #47 - Add Google support
    # This is the relative path from status-light.py
    google_credential_store = './utility/api/calendar/google'
    google_token_store = '~'

    #38 - Working Elsewhere isn't handled
    off_status = [const.Status.inactive, const.Status.outofoffice,
        const.Status.workingelsewhere, const.Status.unknown, const.Status.free]
    available_status = [const.Status.active]
    scheduled_status = [const.Status.busy, const.Status.tentative]
    busy_status = [const.Status.call, const.Status.donotdisturb,
        const.Status.meeting, const.Status.presenting, const.Status.pending]

    available_color = const.Color.green.value
    scheduled_color = const.Color.orange.value
    busy_color = const.Color.red.value

    #22 - Make sleep timeout configurable
    sleep_seconds = 5

    #23 - Make logging level configurable
    log_level = 'WARNING'

    def get_sources(self):
        #32 - SOURCES variable default is wrong
        self.selected_sources = self._parse_source(os.environ.get('SOURCES',
            self.selected_sources))
        return_value = (None is not self.selected_sources)
        #34 - Better environment variable errors
        # SOURCES is required
        if not return_value:
            logger.warning('SOURCES - at least one source is required!')
        return return_value

    def get_tuya(self):
        return_value = True
        # 30: This variable could contain secrets
        self.tuya_device = self._get_env_or_secret('TUYA_DEVICE', None)
        #34 - Better environment variable errors
        # TUYA_DEVICE is required
        if None in [self.tuya_device]:
            logger.warning('TUYA_DEVICE is required!')
            return_value = False

        # 41: Replace decorator with utility function
        self.tuya_brightness = util.try_parse_int(os.environ.get('TUYA_BRIGHTNESS'),
            default = self.tuya_brightness)
        #34 - Better environment variable errors
        # TUYA_BRIGHTNESS should be within the range 32..255
        if self.tuya_brightness < 32 or self.tuya_brightness > 255:
            logger.warning('TUYA_BRIGHTNESS must be between 32 and 255!')
            return_value = False

        return return_value

    def get_webex(self):
        # 30: This variable could contain secrets
        self.webex_person_id = self._get_env_or_secret('WEBEX_PERSONID', None)
        # 30: This variable could contain secrets
        self.webex_bot_id = self._get_env_or_secret('WEBEX_BOTID', None)
        return (None not in [self.webex_person_id, self.webex_bot_id])

    def get_office(self):
        # 30: This variable could contain secrets
        self.office_app_id = self._get_env_or_secret('O365_APPID', None)
        # 30: This variable could contain secrets
        self.office_app_secret = self._get_env_or_secret('O365_APPSECRET', None)
        self.office_token_store = os.environ.get('O365_TOKENSTORE', self.office_token_store)
        return (None not in [self.office_app_id, self.office_app_secret, self.office_token_store])

    #47: Add Google support
    def get_google(self):
        self.google_credential_store = os.environ.get('GOOGLE_CREDENTIALSTORE',
            self.google_credential_store)
        self.google_token_store = os.environ.get('GOOGLE_TOKENSTORE',
            self.google_token_store)
        return (None not in [self.google_credential_store, self.google_token_store])

    def get_colors(self):
        self.available_color = self._parse_color(os.environ.get('AVAILABLE_COLOR', None),
            self.available_color)
        self.scheduled_color = self._parse_color(os.environ.get('SCHEDULED_COLOR', None),
            self.scheduled_color)
        self.busy_color = self._parse_color(os.environ.get('BUSY_COLOR', None),
            self.busy_color)
        return (None not in [self.available_color, self.scheduled_color, self.busy_color])

    def get_status(self):
        self.off_status = self._parse_status(os.environ.get('OFF_STATUS', None),
            self.off_status)
        self.available_status = self._parse_status(os.environ.get('AVAILABLE_STATUS', None),
            self.available_status)
        self.busy_status = self._parse_status(os.environ.get('BUSY_STATUS', None),
            self.busy_status)
        self.scheduled_status = self._parse_status(os.environ.get('SCHEDULED_STATUS', None),
            self.scheduled_status)
        return (None not in [self.off_status, self.available_status,
            self.busy_status, self.scheduled_status])

    def get_sleep(self):
        # 41: Replace decorator with utility function
        self.sleep_seconds = util.try_parse_int(os.environ.get('SLEEP_SECONDS'),
            default = self.sleep_seconds)
        return self.sleep_seconds >= 5 and self.sleep_seconds <= 60

    def get_log_level(self):
        self.log_level = self._parse_log_level(os.environ.get('LOGLEVEL'),
            self.log_level)
        return self.log_level is not None

    def _parse_source(self, source_string):
        temp_status = None
        if source_string in [None, '']:
            return temp_status

        try:
            temp_status = list(const.StatusSource[source.lower().strip()]
                for source in source_string.split(','))
        except BaseException as ex:
            logger.warning('Exception encountered during _parseSource: %s', ex)
            temp_status = None
        return temp_status

    def _parse_color(self, color_string, default):
        temp_color = default
        if color_string in [None, '']:
            return temp_color

        try:
            # We accept both a set of constants [red, green, blue, yellow, orange]
            # or a standard hex RGB (rrggbb) input
            if not re.match('^[0-9A-Fa-f]{6}$', color_string) is None:
                temp_color = color_string
            else:
                temp_color = const.Color[color_string.lower().strip()].value
                if temp_color == const.Color.unknown.value:
                    temp_color = default
        except BaseException as ex:
            logger.warning('Exception encountered during _parseColor: %s, using default: %s',
                ex, default)
            temp_color = default
        return temp_color

    def _parse_status(self, status_string, default):
        temp_status = default
        if status_string in [None, '']:
            return temp_status

        try:
            temp_status = list(const.Status[status.lower().strip()]
                for status in status_string.split(','))
        except BaseException as ex:
            logger.warning('Exception encountered during _parseStatus: %s, using default: %s',
                ex, list(status.name for status in default))
            temp_status = default
        return temp_status

    #23 - Log Level
    def _parse_log_level(self, log_string, default):
        temp_log = default
        if log_string in [None, '']:
            return temp_log

        try:
            # We accept a set of logging constants [CRITICAL, ERROR, WARNING, INFO, DEBUG]
            if not re.match('^(CRITICAL|ERROR|WARNING|INFO|DEBUG)$',
                log_string.upper().strip()) is None:

                temp_log = log_string.upper().strip()
            else:
                temp_log = default
        except BaseException as ex:
            logger.warning('Exception encountered during _parseLogLevel: %s, using default: %s',
                ex, default)
            temp_log = default

        return temp_log

    # 30 - Docker Secrets
    def _get_env_or_secret(self, variable, default, treat_empty_as_none: bool = True):
        """Given a variable name, returns the Environment or File variant of the variable.
        If both are None, returns default.

        For a given variable name, e.g. O365_APPSECRET, this method will check for both
        the standard environment variable (O365_APPSECRET) as well as the _FILE variant
        (O365_APPSECRET_FILE).

        Precedence is given to the standard environment variable, and the _FILE variant
        is only checked if the standard variant is nonexistent or None.
        If treat_empty_as_none is true (which is the default), this method will also treat
        empty strings returned from either variant as None, and trigger the next check
        or return the default.

        Note that this method does not attempt to parse or validate the value in variable;
        it simply returns the raw string found, if any.
        """
        value = default
        try:
            # First, check the standard variant
            value = os.environ.get(variable, None)

            # If this value is None or an empty string,
            if value is None or (treat_empty_as_none and value == ''):
                # Check the _FILE variant
                secret_filename = os.environ.get(variable + '_FILE', None)
                if secret_filename is not None and (treat_empty_as_none and value != ''):
                    value = self._read_file(secret_filename)
            else:
                # Strip the whitespace
                value = value.strip()
        except BaseException as ex:
            logger.warning('Exception encountered during _getEnvOrSecret for %s: %s', variable, ex)
            value = default

        # Finally, if the value is nonexistent or empty, just return the default
        if value is None or (treat_empty_as_none and value == ''):
            value = default

        return value

    def _read_file(self, file, strip: bool = True):
        """Read, and optionally strip spaces from, a file."""
        secret = None

        if not os.access(file, os.F_OK):
            return secret
        else:
            try:
                with open(file, encoding='platform') as file:
                    secret = file.read()
                    if strip:
                        secret = secret.strip()
            except BaseException as ex:
                logger.warning('Exception encountered during _readFile: %s', ex)

        return secret
