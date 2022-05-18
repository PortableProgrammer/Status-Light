"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Webex Teams Source
"""

# Standard imports
import logging

# 3rd-Party imports
from webexteamssdk import WebexTeamsAPI

# Project imports
from utility import enum

logger = logging.getLogger(__name__)

class WebexAPI:
    botID = ""

    def get_person_status(self, person_id):
        api = WebexTeamsAPI(access_token = self.botID)
        try:
            return enum.Status[api.people.get(person_id).status.lower()]
        except (SystemExit, KeyboardInterrupt):
            pass
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception during getPersonStatus: %s', ex)
            return "unknown"
