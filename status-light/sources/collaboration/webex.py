"""Status-Light
(c) 2020-2023 Nick Warner
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
    """Wraps the `webexteamssdk.WebexTeamsAPI` class"""
    bot_id = ''
    person_id: str = ''

    def get_person_status(self) -> enum.Status:
        """Retrieves the Webex Teams status for the defined `person_id`"""
        api = WebexTeamsAPI(access_token=self.bot_id)
        return_value = enum.Status.UNKNOWN
        try:
            return_value = enum.Status[api.people.get(
                self.person_id).status.lower()]
        except (SystemExit, KeyboardInterrupt):
            pass
        except Exception as ex: # pylint: disable=broad-except
            logger.warning(
                'Exception while getting Webex person status: %s', ex)
            logger.exception(ex)
            return_value = enum.Status.UNKNOWN

        return return_value
