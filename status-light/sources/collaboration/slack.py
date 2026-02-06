"""Status-Light
(c) 2020-2026 Nick Warner
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
    """Wraps the `slack_sdk.web.WebClient` class"""
    user_id: str = ''
    bot_token: str = ''
    # 66 - Support Slack custom statuses
    custom_available_status: list[str] = []
    custom_available_status_map: enum.Status = enum.Status.UNKNOWN
    custom_busy_status: list[str] = []
    custom_busy_status_map: enum.Status = enum.Status.UNKNOWN
    custom_scheduled_status: list[str] = []
    custom_scheduled_status_map: enum.Status = enum.Status.UNKNOWN
    custom_off_status: list[str] = []
    custom_off_status_map: enum.Status = enum.Status.UNKNOWN

    def get_user_presence(self) -> enum.Status:
        """Retrieves the user presence info for the defined `user_id`"""
        client = self._get_client()
        response = None
        return_value = enum.Status.UNKNOWN
        try:
            # 66: Support Slack custom statuses
            return_value = self._parse_custom_status(client)

            if return_value is enum.Status.UNKNOWN:
                response = client.users_getPresence(user=self.user_id)
                match response.data['presence']:  # type: ignore
                    case "active":
                        return_value = enum.Status.ACTIVE
                    case "away":
                        return_value = enum.Status.INACTIVE
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning(
                'Slack Exception while getting user presence: %s', ex.response['error'])
            logger.exception(ex)
            return_value = enum.Status.UNKNOWN
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(
                'Exception while getting Slack user presence: %s', ex)
            logger.exception(ex)
            return_value = enum.Status.UNKNOWN

        return return_value

    def _get_client(self) -> WebClient:
        """Internal Helper Method to build and return a Slack `WebClient` object."""
        return WebClient(token=self.bot_token)

    def _get_user_info(self, client: WebClient) -> dict | None:
        """Internal Helper Method to retrieve user info for the class' defined `user_id`"""
        response = None
        try:
            response = client.users_info(user=self.user_id)
            return response.data['user']  # type: ignore
        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning(
                'Slack Exception while getting user info: %s', ex.response['error'])
            logger.exception(ex)
            return None
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Exception while getting Slack user info: %s', ex)
            logger.exception(ex)
            return None

    def _parse_custom_status(self, client: WebClient,
                             default: enum.Status = enum.Status.UNKNOWN) -> enum.Status:
        """Internal Helper Method to parse a user's custom status value into a `Status` enum."""
        return_value = default

        try:
            # Get the latest user info
            user_info = self._get_user_info(client)

            if not user_info or not user_info['profile']:
                return enum.Status.UNKNOWN

            # Join the emoji and text with a space
            custom_status: str = (user_info['profile']['status_emoji'] + ' '
                                  + user_info['profile']['status_text']).casefold()

            # For each of the Slack custom statuses, check them in reverse precedence order
            # Off, Available, Scheduled, Busy
            if len(self.custom_off_status) > 0 and \
                    custom_status.startswith(tuple(self.custom_off_status)):
                logger.debug(
                    'Custom status matched custom_off_status: %s', custom_status)
                return_value = self.custom_off_status_map

            if len(self.custom_available_status) > 0 and \
                    custom_status.startswith(tuple(self.custom_available_status)):
                logger.debug(
                    'Custom status matched custom_available_status: %s', custom_status)
                return_value = self.custom_available_status_map

            if len(self.custom_scheduled_status) > 0 and \
                    custom_status.startswith(tuple(self.custom_scheduled_status)):
                logger.debug(
                    'Custom status matched custom_scheduled_status: %s', custom_status)
                return_value = self.custom_scheduled_status_map

            if len(self.custom_busy_status) > 0 and \
                    custom_status.startswith(tuple(self.custom_busy_status)):
                logger.debug(
                    'Custom status matched custom_busy_status: %s', custom_status)
                return_value = self.custom_busy_status_map

            # Check for Huddle and Call
            if user_info['profile']['huddle_state'] == 'in_a_huddle' or \
                    user_info['profile']['status_emoji'] == ':slack_call:':
                logger.debug('Custom status indicates Huddle (%s) or Call (%s)',
                             user_info['profile']['huddle_state'], custom_status)
                return_value = enum.Status.CALL

        except (SystemExit, KeyboardInterrupt):
            pass
        except SlackApiError as ex:
            logger.warning(
                'Slack Exception while parsing custom status: %s', ex.response['error'])
            logger.exception(ex)
            return_value = enum.Status.UNKNOWN
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(
                'Exception while parsing Slack custom status: %s', ex)
            logger.exception(ex)
            return_value = enum.Status.UNKNOWN

        return return_value
