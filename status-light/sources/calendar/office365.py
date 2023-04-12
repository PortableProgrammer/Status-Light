"""Status-Light
(c) 2020-2023 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Office 365 Source
"""

# Standard imports
from datetime import datetime
from datetime import timedelta
import logging

# 3rd-party imports
from O365 import Account
from O365 import FileSystemTokenBackend

# Project imports
from utility import enum

logger = logging.getLogger(__name__)


class OfficeAPI:
    """Wraps the `O365.Account` class"""
    appID = ''
    appSecret = ''
    tokenStore = '~'
    account: Account

    def authenticate(self):
        """Authenticates against Office 365"""
        token_backend = FileSystemTokenBackend(token_path=self.tokenStore,
                                               token_filename='o365_token.txt')
        self.account = Account((self.appID, self.appSecret),
                               token_backend=token_backend)
        if not self.account.is_authenticated:
            self.account.authenticate(scopes=['basic', 'calendar'])

    def get_schedule(self):
        """Retrieves the current Account's Schedule"""
        self.authenticate()
        return self.account.schedule()

    def get_calendar(self):
        """Retrieves the current Account's Calendar from their Schedule"""
        self.authenticate()
        return self.account.schedule().get_default_calendar()

    def get_current_status(self):
        """Retrieves the Office 365 status within the next 5 minutes"""
        try:
            schedule = self.get_schedule()
            schedules = [self.account.get_current_user().mail]  # type: ignore
            availability = schedule.get_availability(schedules, datetime.now(),
                                                     datetime.now() + timedelta(minutes=5), 5)
            availability_view = availability[0]["availabilityView"][0]
            logger.debug('Got availabilityView: %s', availability_view)

            return enum.Status[availability_view.replace(' ', '').lower()]
        except (SystemExit, KeyboardInterrupt):
            return enum.Status.UNKNOWN
        except Exception as ex: # pylint: disable=broad-except
            logger.warning('Exception while getting Office 365 status: %s', ex)
            logger.exception(ex)
            return enum.Status.UNKNOWN
