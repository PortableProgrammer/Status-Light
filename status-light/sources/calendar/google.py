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
        normalizedTokenPath = os.path.normpath(self.tokenStore + '/token.json')
        normalizedCredentialsPath = os.path.normpath(self.credentialStore + '/' + self.CREDENTIALS_FILENAME)
        if os.path.exists(normalizedTokenPath):
            creds = Credentials.from_authorized_user_file(normalizedTokenPath, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(normalizedCredentialsPath, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(normalizedTokenPath, 'w') as token:
                token.write(creds.to_json())
        return creds

    def getCalendarService(self):
        creds = self.authenticate()

        service = build('calendar', 'v3', credentials=creds)
        return service

    def getCurrentStatus(self):
        try:
            service = self.getCalendarService()
            now = datetime.utcnow().isoformat() + 'Z'
            now_plus = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + 'Z'
            #freebusy_result = service.freebusy().query(items=[{"id": 'primary'}],timeMin=now, timeMax=now_plus).execute()
            query = {
                "timeMin" : now,
                "timeMax" : now_plus,
                "items" : [
                    {
                        "id" : "primary"
                    }
                ]
            }
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
        except BaseException as e:
            logger.warning('Exception during GoogleAPI.getCurrentStatus: %s',e)
            # TODO: Don't be stupid, fix this
            return const.Status.unknown