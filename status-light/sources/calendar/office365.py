"""Status-Light
(c) 2020-2022 Nick Warner
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
    appID = ''
    appSecret = ''
    tokenStore = '~'
    account = None

    def authenticate(self):
        token_backend = FileSystemTokenBackend(token_path=self.tokenStore,
            token_filename='o365_token.txt')
        self.account = Account((self.appID, self.appSecret), token_backend = token_backend)
        if not self.account.is_authenticated:
            self.account.authenticate(scopes = ['basic', 'calendar'])

    def get_schedule(self):
        self.authenticate()
        return self.account.schedule()

    def get_calendar(self):
        self.authenticate()
        return self.account.schedule().get_default_calendar()

    def get_current_status(self):
        try:
            schedule = self.get_schedule()
            schedules = [self.account.get_current_user().mail]
            availability = schedule.get_availability(schedules, datetime.now(),
                datetime.now() + timedelta(minutes=5), 5)
            availability_view = availability[0]["availabilityView"][0]
            logger.debug('Got availabilityView: %s', availability_view)

            return enum.Status[availability_view.replace(' ','').lower()]
        except (SystemExit, KeyboardInterrupt):
            return enum.Status.UNKNOWN
        except BaseException as ex: # pylint: disable=broad-except
            logger.warning('Exception during OfficeAPI.getCurrentStatus: %s', ex)
            return enum.Status.UNKNOWN
