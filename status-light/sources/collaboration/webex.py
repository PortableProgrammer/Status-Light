# https://github.com/portableprogrammer/Status-Light/

# Standard imports
import logging

# 3rd-Party imports
from webexteamssdk import WebexTeamsAPI

# Project imports
from utility import const

logger = logging.getLogger(__name__)

class WebexAPI:
    botID = ""

    def get_person_status(self, person_id):
        api = WebexTeamsAPI(access_token = self.botID)
        try:
            return const.Status[api.people.get(person_id).status.lower()]
        except (SystemExit, KeyboardInterrupt):
            pass
        except BaseException as ex:
            logger.warning('Exception during getPersonStatus: %s', ex)
            return "unknown"
