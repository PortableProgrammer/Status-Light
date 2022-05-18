# https://github.com/portableprogrammer/Status-Light/

# Standard imports
import logging

# 3rd-Party imports
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

# Project imports
from utility import const

logger = logging.getLogger(__name__)

class SlackAPI:
    user_id = None
    bot_token = None

    def get_client(self):
        return WebClient(token=self.bot_token)

    def get_user_info(self, client:WebClient = None):
        response = None
        if client is None:
            client = self.get_client()
        try:
            response = client.users_info(user=self.user_id) # pylint: disable=no-value-for-parameter

            return response.data['user'] # pylint: disable=no-member
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning('Exception during get_user_info: %s', ex.response['error'])
            return None
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception during get_user_info: %s', ex)
            return None

    def get_user_presence(self, check_dnd:bool=True, check_huddle:bool=True):
        client = self.get_client()
        response = None
        user_info = None
        return_value = const.Status.unknown
        try:
            # If we want to check for DnD or Huddle (busy or call),
            if check_dnd or check_huddle:
                # Get the latest user info
                user_info = self.get_user_info(client)
                if user_info['profile']['status_emoji'] == ':headphones:' \
                    and user_info['profile']['status_text'].startsWith('In a huddle'):

                    return_value = const.Status.meeting

            if return_value is const.Status.unknown:
                response = client.users_getPresence(user=self.user_id)
                match response.data['presence']: # pylint: disable=no-member
                    case "active":
                        return_value = const.Status.active
                    case "away":
                        return_value = const.Status.inactive
            return return_value
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning('Exception during get_user_info: %s', ex.response['error'])
            return const.Status.unknown
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception during get_user_presence: %s', ex)
            return const.Status.unknown
