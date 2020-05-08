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
        tuyaDevice = os.environ.get(self.TUYA_DEVICE, None)
        return (None not in [tuyaDevice])

    def getWebex(self):
        webexPersonID = os.environ.get(self.WEBEX_PERSONID, None)
        webexBotID = os.environ.get(self.WEBEX_BOTID, None)
        return (None not in [webexPersonID, webexBotID])

    def getOffice(self):
        officeAppId = os.environ.get(self.O365_APPID, None)
        officeAppSecret = os.environ.get(self.O365_APPSECRET, None)
        officeTokenStore = os.environ.get(self.O365_TOKENSTORE, '~')
        return (None not in [officeAppId, officeAppSecret, officeTokenStore])
