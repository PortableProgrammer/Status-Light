# https://github.com/portableprogrammer/Status-Light/

import enum
from webexteamssdk import WebexTeamsAPI
import logging

# Project imports
import const

logger = logging.getLogger(__name__)

class WebexAPI:
    botKey = ""

    def getPersonStatus(self, personId):
        api = WebexTeamsAPI(access_token = self.botKey)
        try:
            return const.Status[api.people.get(personId).status]
        except BaseException as e:
            logger.warning('Exception during getPersonStatus:',e)
            return "unknown"
