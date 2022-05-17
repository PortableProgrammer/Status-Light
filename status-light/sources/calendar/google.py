#47: Add Google Calendar support
# https://github.com/portableprogrammer/Status-Light/

# Standard imports
import os.path
from datetime import datetime
from datetime import timedelta
import logging

# 3rd-party imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Project imports
from utility import const

logger = logging.getLogger(__name__)

class GoogleAPI:
    credentialStore = '~'
    tokenStore = '~'

    CREDENTIALS_FILENAME = 'client_secret.json'

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def authenticate(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        norm_token_path = os.path.normpath(self.tokenStore + '/token.json')
        norm_cred_path = os.path.normpath(self.credentialStore + '/' + self.CREDENTIALS_FILENAME)
        if os.path.exists(norm_token_path):
            creds = Credentials.from_authorized_user_file(norm_token_path, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(norm_cred_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # Per the docs, encoding should only be used in 'text' mode, which we are not.
            # pylint: disable=unspecified-encoding
            with open(norm_token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def get_calendar_service(self):
        creds = self.authenticate()

        service = build('calendar', 'v3', credentials=creds)
        return service

    def get_current_status(self):
        try:
            service = self.get_calendar_service()
            now = datetime.utcnow().isoformat() + 'Z'
            now_plus = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + 'Z'
            query = {
                "timeMin" : now,
                "timeMax" : now_plus,
                "items" : [
                    {
                        "id" : "primary"
                    }
                ]
            }
            # Since the service instance of Resource is dynamically-generated,
            # Pylint has no member definitions; ignore the 'no-member' error
            # pylint: disable=no-member
            freebusy_result = service.freebusy().query(body=query).execute()
            logger.debug('Got Free/Busy Result: %s', freebusy_result)
            freebusy = freebusy_result['calendars']['primary']['busy']
            if freebusy and len(freebusy) > 0:
                logger.debug('Found Busy Result: %s', freebusy)
                return const.Status.busy
            else:
                logger.debug('No Free/Busy Result, assuming Free')
                return const.Status.free
        except (SystemExit, KeyboardInterrupt):
            return const.Status.unknown
        except BaseException as exc:
            logger.warning('Exception during GoogleAPI.getCurrentStatus: %s', exc)
            return const.Status.unknown
