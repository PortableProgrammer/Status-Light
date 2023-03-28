"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Google Calendar Source
"""

# 47: Add Google Calendar support
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
from utility import enum

logger = logging.getLogger(__name__)


class GoogleCalendarAPI:
    """Handles Google Calendar Free/Busy"""

    credentialStore = '~'
    tokenStore = '~'

    CREDENTIALS_FILENAME = 'client_secret.json'

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.freebusy']

    def authenticate(self):
        """Authenticates the user against the Google Calendar API.

        Returns the authenticated credentials."""
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        norm_token_path = os.path.normpath(self.tokenStore + '/token.json')
        norm_cred_path = os.path.normpath(
            self.credentialStore + '/' + self.CREDENTIALS_FILENAME)
        if os.path.exists(norm_token_path):
            creds = Credentials.from_authorized_user_file(
                norm_token_path, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    norm_cred_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # Per the docs, encoding should only be used in 'text' mode, which we are not.
            # pylint: disable=unspecified-encoding
            with open(norm_token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def get_calendar_service(self):
        """Builds the Google Calendar service object.

        Returns the Calendar service object."""
        creds = self.authenticate()

        service = build('calendar', 'v3', credentials=creds)
        return service

    def get_current_status(self):
        """Connects to the Google Calendar API to retrieve the user's free/busy
        status within the next 5 minutes.

        Returns the status returned from Google, or 'unknown' if an error occurs."""
        try:
            service = self.get_calendar_service()
            now = datetime.utcnow().isoformat() + 'Z'
            now_plus = (datetime.utcnow() +
                        timedelta(minutes=5)).isoformat() + 'Z'
            query = {
                "timeMin": now,
                "timeMax": now_plus,
                "items": [
                    {
                        "id": "primary"
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
                return enum.Status.BUSY
            else:
                logger.debug('No Free/Busy Result, assuming Free')
                return enum.Status.FREE
        except (SystemExit, KeyboardInterrupt):
            return enum.Status.UNKNOWN
        except BaseException as ex:  # pylint: disable=broad-except
            logger.warning('Exception while getting Google status: %s', ex)
            return enum.Status.UNKNOWN
