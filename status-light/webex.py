# https://github.com/portableprogrammer/Status-Light/

import enum
from webexteamssdk import WebexTeamsAPI
import logging

# Project imports
import const

logger = logging.getLogger(__name__)

class WebexAPI:
    botID = ""

    def getPersonStatus(self, personID):
        api = WebexTeamsAPI(access_token = self.botID)
        try:
            return const.Status[api.people.get(personID).status]
        except BaseException as e:
            logger.warning('Exception during getPersonStatus: %s',e)
            return "unknown"
