import os
import re
import logging

import const
import util

logger = logging.getLogger(__name__)

class Environment:
    tuyaDevice = None
    tuyaBrightness = 128

    selectedSources = None

    webexPersonID = None
    webexBotID = None

    officeAppID = None
    officeAppSecret = None
    officeTokenStore = '~'

    offStatus = [const.Status.inactive, const.Status.outofoffice, const.Status.unknown, const.Status.free]
    availableStatus = [const.Status.active]
    scheduledStatus = [const.Status.busy, const.Status.tentative]
    busyStatus = [const.Status.call, const.Status.donotdisturb, const.Status.meeting, const.Status.presenting, const.Status.pending]

    availableColor = const.Color.green.value
    scheduledColor = const.Color.orange.value
    busyColor = const.Color.red.value

    def getSources(self):
        self.selectedSources = self._parseSource(os.environ.get('SOURCES', None))
        return (None != self.selectedSources)

    def getTuya(self):
        self.tuyaDevice = os.environ.get('TUYA_DEVICE', None)
        brightness_try_parse = util.ignore_exception(ValueError, self.tuyaBrightness)(int)
        self.tuyaBrightness = brightness_try_parse(os.environ.get('TUYA_BRIGHTNESS', self.tuyaBrightness))
        return (None not in [self.tuyaDevice]) and self.tuyaBrightness >= 32 and self.tuyaBrightness <= 255

    def getWebex(self):
        self.webexPersonID = os.environ.get('WEBEX_PERSONID', None)
        self.webexBotID = os.environ.get('WEBEX_BOTID', None)
        return (None not in [self.webexPersonID, self.webexBotID])

    def getOffice(self):
        self.officeAppID = os.environ.get('O365_APPID', None)
        self.officeAppSecret = os.environ.get('O365_APPSECRET', None)
        self.officeTokenStore = os.environ.get('O365_TOKENSTORE', self.officeTokenStore)
        return (None not in [self.officeAppID, self.officeAppSecret, self.officeTokenStore])

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

    def _parseSource(self, sourceString):
        tempStatus = None
        if sourceString in [None, '']: 
            return tempStatus

        try:
            tempStatus = list(const.StatusSource[source.lower().strip()] for source in sourceString.split(','))
        except BaseException as e:
            logger.warning('Exception encountered during _parseSourcr: %s', e)
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
