# https://github.com/portableprogrammer/Status-Light/

from O365 import Account

class OfficeAPI:
    appID = ''
    appSecret = ''
    account = None

    def authenticate(self):
        credentials = (appID, appSecret)

        account = Account(credentials)
        if account.authenticate(scopes=['basic', 'calendar']):
            print('Authenticated!')