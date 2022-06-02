"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Slack Source
"""

# Standard imports
import logging

# 3rd-Party imports
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

# Project imports
from utility import enum

logger = logging.getLogger(__name__)

class SlackAPI:
    user_id = None
    bot_token = None
    # 66 - Support Slack custom statuses
    custom_available_status = None
    custom_available_status_map = None
    custom_busy_status = None
    custom_busy_status_map = None
    custom_scheduled_status = None
    custom_scheduled_status_map = None
    custom_off_status = None
    custom_off_status_map = None

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
            logger.warning('Slack Exception while getting user info: %s', ex.response['error'])
            return None
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception while getting Slack user info: %s', ex)
            return None

    def get_user_presence(self):
        client = self.get_client()
        response = None
        return_value = enum.Status.UNKNOWN
        try:
            # 66: Support Slack custom statuses
            return_value = self._parse_custom_status(client)

            if return_value is enum.Status.UNKNOWN:
                response = client.users_getPresence(user=self.user_id)
                match response.data['presence']: # pylint: disable=no-member
                    case "active":
                        return_value = enum.Status.ACTIVE
                    case "away":
                        return_value = enum.Status.INACTIVE
            return return_value
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning('Slack Exception while getting user presence: %s', ex.response['error'])
            return enum.Status.UNKNOWN
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception while getting Slack user presence: %s', ex)
            return enum.Status.UNKNOWN

    def _parse_custom_status(self, client:WebClient,  default:enum.Status = enum.Status.UNKNOWN):
        return_value = default

        try:
            # Get the latest user info
            user_info = self.get_user_info(client)
            # Join the emoji and text with a space
            custom_status = user_info['profile']['status_emoji'] + ' ' + user_info['profile']['status_text']

            # For each of the Slack custom statuses, check them in reverse precedence order
            # Off, Available, Scheduled, Busy
            if custom_status.startswith(tuple(self.custom_off_status)):
                return_value = self.custom_off_status_map

            if custom_status.startswith(tuple(self.custom_available_status)):
                return_value = self.custom_available_status_map

            if custom_status.startswith(tuple(self.custom_scheduled_status)):
                return_value = self.custom_scheduled_status_map

            if custom_status.startswith(tuple(self.custom_busy_status)):
                return_value = self.custom_busy_status_map

            return return_value
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning('Slack Exception while parsing custom status: %s', ex.response['error'])
            return enum.Status.UNKNOWN
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception while parsing Slack custom status: %s', ex)
            return enum.Status.UNKNOWN
