# https://github.com/portableprogrammer/Status-Light/

from O365 import Account
from O365 import FileSystemTokenBackend
from datetime import datetime 
from datetime import timedelta
import logging

# Project imports
import const

logger = logging.getLogger(__name__)

class OfficeAPI:
    appID = ''
    appSecret = ''
    tokenStore = '~'
    account = None

    def authenticate(self):
        token_backend = FileSystemTokenBackend(token_path = self.tokenStore, token_filename = 'o365_token.txt')
        self.account = Account((self.appID, self.appSecret), token_backend = token_backend)
        if not self.account.is_authenticated:
            self.account.authenticate(scopes = ['basic', 'calendar'])

    def getSchedule(self):
        self.authenticate()
        return self.account.schedule()

    def getCalendar(self):
        self.authenticate()
        return self.account.schedule().get_default_calendar()

    def getCurrentStatus(self):
        try: 
            schedule = self.getSchedule()
            schedules = [self.account.get_current_user().mail]
            availability = schedule.get_availability(schedules, datetime.now(), datetime.now() + timedelta(minutes=5), 5)
            availabilityView = availability[0]["availabilityView"][0]
            logger.debug('Got availabilityView: %s', availabilityView)

            # Issue #3: Handle all O365 Statuses
            # The OutOfOffice status is returned as a string with spaces, unlike the rest of the statuses, so we need to treat it special
            if availabilityView == 'out of office':
                availabilityView = 'OutOfOffice'
            # The WorkingElsewhere status is returned as a string with spaces, unlike the rest of the statuses, so we need to treat it special
            if availabilityView == 'working elsewhere':
                availabilityView = 'WorkingElsewhere'

            return const.Status[availabilityView]
        except (SystemExit, KeyboardInterrupt):
            return const.Status.unknown
        except BaseException as e:
            logger.warning('Exception during OfficeAPI.getCurrentStatus: %s',e)
            # TODO: Don't be stupid, fix this
            return const.Status.unknown