import os
import logging

logger = logging.getLogger(__name__)

class Environment:
    tuyaDevice = None
    TUYA_DEVICE = 'TUYA_DEVICE'

    webexPersonID = None
    webexBotID = None
    WEBEX_PERSONID = 'WEBEX_PERSONID'
    WEBEX_BOTID = 'WEBEX_BOTID'

    officeAppID = None
    officeAppSecret = None
    officeTokenStore = None
    O365_APPID = 'O365_APPID'
    O365_APPSECRET = 'O365_APPSECRET'
    O365_TOKENSTORE = 'O365_TOKENSTORE'

    def getTuya(self):
        self.tuyaDevice = os.environ.get(self.TUYA_DEVICE, None)
        return (None not in [self.tuyaDevice])

    def getWebex(self):
        self.webexPersonID = os.environ.get(self.WEBEX_PERSONID, None)
        self.webexBotID = os.environ.get(self.WEBEX_BOTID, None)
        return (None not in [self.webexPersonID, self.webexBotID])

    def getOffice(self):
        self.officeAppID = os.environ.get(self.O365_APPID, None)
        self.officeAppSecret = os.environ.get(self.O365_APPSECRET, None)
        self.officeTokenStore = os.environ.get(self.O365_TOKENSTORE, '~')
        return (None not in [self.officeAppID, self.officeAppSecret, self.officeTokenStore])
