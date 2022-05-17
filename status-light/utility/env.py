import os
import re
import logging

from utility import const
from utility import util

logger = logging.getLogger(__name__)

class Environment:
    tuyaDevice = None
    tuyaBrightness = 128

    #32 - SOURCES variable default is wrong
    #32 Recurred; _parseSource expects a string, not a list. Convert the list to a string.
    selectedSources = 'Webex,Office365'

    webexPersonID = None
    webexBotID = None

    officeAppID = None
    officeAppSecret = None
    officeTokenStore = '~'

    #47 - Add Google support
    googleCredentialStore = '~'
    googleTokenStore = '~'

    #38 - Working Elsewhere isn't handled
    offStatus = [const.Status.inactive, const.Status.outofoffice, const.Status.workingelsewhere, const.Status.unknown, const.Status.free]
    availableStatus = [const.Status.active]
    scheduledStatus = [const.Status.busy, const.Status.tentative]
    busyStatus = [const.Status.call, const.Status.donotdisturb, const.Status.meeting, const.Status.presenting, const.Status.pending]

    availableColor = const.Color.green.value
    scheduledColor = const.Color.orange.value
    busyColor = const.Color.red.value

    #22 - Make sleep timeout configurable
    sleepSeconds = 5

    #23 - Make logging level configurable
    logLevel = 'WARNING'

    def getSources(self):
        #32 - SOURCES variable default is wrong
        self.selectedSources = self._parseSource(os.environ.get('SOURCES', self.selectedSources))
        returnValue = (None != self.selectedSources)
        #34 - Better environment variable errors
        # SOURCES is required
        if not returnValue:
            logger.warning('SOURCES - at least one source is required!')
        return returnValue

    def getTuya(self):
        returnValue = True
        # 30: This variable could contain secrets
        self.tuyaDevice = self._getEnvOrSecret('TUYA_DEVICE', None)
        #34 - Better environment variable errors
        # TUYA_DEVICE is required
        if (None in [self.tuyaDevice]):
            logger.warning('TUYA_DEVICE is required!')
            returnValue = False

        # 41: Replace decorator with utility function
        self.tuyaBrightness = util.try_parse_int(os.environ.get('TUYA_BRIGHTNESS'), default = self.tuyaBrightness)
        #34 - Better environment variable errors
        # TUYA_BRIGHTNESS should be within the range 32..255
        if self.tuyaBrightness < 32 or self.tuyaBrightness > 255:
            logger.warning('TUYA_BRIGHTNESS must be between 32 and 255!')
            returnValue = False

        return returnValue

    def getWebex(self):
        # 30: This variable could contain secrets
        self.webexPersonID = self._getEnvOrSecret('WEBEX_PERSONID', None)
        # 30: This variable could contain secrets
        self.webexBotID = self._getEnvOrSecret('WEBEX_BOTID', None)
        return (None not in [self.webexPersonID, self.webexBotID])

    def getOffice(self):
        # 30: This variable could contain secrets
        self.officeAppID = self._getEnvOrSecret('O365_APPID', None)
        # 30: This variable could contain secrets
        self.officeAppSecret = self._getEnvOrSecret('O365_APPSECRET', None)
        self.officeTokenStore = os.environ.get('O365_TOKENSTORE', self.officeTokenStore)
        return (None not in [self.officeAppID, self.officeAppSecret, self.officeTokenStore])

    #47: Add Google support
    def getGoogle(self):
        self.googleCredentialStore = self._getEnvOrSecret('GOOGLE_CREDENTIALSTORE', self.googleCredentialStore)
        self.googleTokenStore = os.environ.get('GOOGLE_TOKENSTORE', self.googleTokenStore)
        return (None not in [self.googleCredentialStore, self.googleTokenStore])

    def getColors(self):
        self.availableColor = self._parseColor(os.environ.get('AVAILABLE_COLOR', None), self.availableColor)
        self.scheduledColor = self._parseColor(os.environ.get('SCHEDULED_COLOR', None), self.scheduledColor)
        self.busyColor = self._parseColor(os.environ.get('BUSY_COLOR', None), self.busyColor)
        return (None not in [self.availableColor, self.scheduledColor, self.busyColor])

    def getStatus(self):
        self.offStatus = self._parseStatus(os.environ.get('OFF_STATUS', None), self.offStatus)
        self.availableStatus = self._parseStatus(os.environ.get('AVAILABLE_STATUS', None), self.availableStatus)
        self.busyStatus = self._parseStatus(os.environ.get('BUSY_STATUS', None), self.busyStatus)
        self.scheduledStatus = self._parseStatus(os.environ.get('SCHEDULED_STATUS', None), self.scheduledStatus)
        return (None not in [self.offStatus, self.availableStatus, self.busyStatus, self.scheduledStatus])

    def getSleep(self):
        # 41: Replace decorator with utility function
        self.sleepSeconds = util.try_parse_int(os.environ.get('SLEEP_SECONDS'), default = self.sleepSeconds)
        return self.sleepSeconds >= 5 and self.sleepSeconds <= 60

    def getLogLevel(self):
        self.logLevel = self._parseLogLevel(os.environ.get('LOGLEVEL'), self.logLevel)
        return self.logLevel != None

    def _parseSource(self, sourceString):
        tempStatus = None
        if sourceString in [None, '']: 
            return tempStatus

        try:
            tempStatus = list(const.StatusSource[source.lower().strip()] for source in sourceString.split(','))
        except BaseException as e:
            logger.warning('Exception encountered during _parseSource: %s', e)
            tempStatus = None
        return tempStatus

    def _parseColor(self, colorString, default):
        tempColor = default
        if colorString in [None, '']: 
            return tempColor

        try:
            # We accept both a set of constants [red, green, blue, yellow, orange] or a standard hex RGB (rrggbb) input
            if not re.match('^[0-9A-Fa-f]{6}$', colorString) == None:
                tempColor = colorString
            else:
                tempColor = const.Color[colorString.lower().strip()].value
                if tempColor == const.Color.unknown.value:
                    tempColor = default
        except BaseException as e:
            logger.warning('Exception encountered during _parseColor: %s, using default: %s', e, default)
            tempColor = default
        return tempColor

    def _parseStatus(self, statusString, default):
        tempStatus = default
        if statusString in [None, '']: 
            return tempStatus

        try:
            tempStatus = list(const.Status[status.lower().strip()] for status in statusString.split(','))
        except BaseException as e:
            logger.warning('Exception encountered during _parseStatus: %s, using default: %s', e, list(status.name for status in default))
            tempStatus = default
        return tempStatus

    #23 - Log Level
    def _parseLogLevel(self, logString, default):
        tempLog = default
        if logString in [None, '']: 
            return tempLog

        try:
            # We accept a set of logging constants [CRITICAL, ERROR, WARNING, INFO, DEBUG]
            if not re.match('^(CRITICAL|ERROR|WARNING|INFO|DEBUG)$', logString.upper().strip()) == None:
                tempLog = logString.upper().strip()
            else:
                tempLog = default
        except BaseException as e:
            logger.warning('Exception encountered during _parseLogLevel: %s, using default: %s', e, default)
            tempLog = default
            
        return tempLog

    # 30 - Docker Secrets
    def _getEnvOrSecret(self, variable, default, treatEmptyAsNone: bool = True):
        """Given a variable name, returns the Environment or File variant of the variable. If both are None, returns default.
        
        For a given variable name, e.g. O365_APPSECRET, this method will check for both the standard environment variable (O365_APPSECRET) as well as the _FILE variant (O365_APPSECRET_FILE).
        Precedence is given to the standard environment variable, and the _FILE variant is only checked if the standard variant is nonexistent or None.
        If treatEmptyAsNone is true (which is the default), this method will also treat empty strings returned from either variant as None, and trigger the next check or return the default.
        Note that this method does not attempt to parse or validate the value in variable; it simply returns the raw string found, if any.
        """
        value = default
        try: 
            # First, check the standard variant
            value = os.environ.get(variable, None)

            # If this value is None or an empty string,
            if value is None or (treatEmptyAsNone and value == ''):
                # Check the _FILE variant
                secretFilename = os.environ.get(variable + '_FILE', None)
                if secretFilename is not None and (treatEmptyAsNone and value != ''):
                    value = self._readFile(secretFilename)
            else:
                # Strip the whitespace
                value = value.strip()
        except BaseException as e:
            logger.warning('Exception encountered during _getEnvOrSecret for %s: %s', variable, e)
            value = default

        # Finally, if the value is nonexistent or empty, just return the default
        if value is None or (treatEmptyAsNone and value == ''):
            value = default

        return value

    def _readFile(self, file, strip: bool = True):
        """Read, and optionally strip spaces from, a file."""
        secret = None

        if not os.access(file, os.F_OK):
            return secret
        else:
            try:
                with open(file) as file:
                    secret = file.read()
                    if (strip):
                        secret = secret.strip()
            except BaseException as e:
                logger.warning('Exception encountered during _readFile: %s', e)

        return secret
