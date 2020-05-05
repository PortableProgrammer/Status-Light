# https://github.com/portableprogrammer/Status-Light/

import enum
from webexteamssdk import WebexTeamsAPI
import const

class WebexAPI:
    botKey = ""

    def getPersonStatus(self, personId):
        api = WebexTeamsAPI(access_token = self.botKey)
        try:
            #return PersonStatus[api.people.get(personId).status]
            return const.Status[api.people.get(personId).status]
        except:
            return "unknown"

# https://developer.webex.com/docs/api/v1/people/get-person-details
class PersonStatus(enum.Enum):
    active = 1
    call = 2
    DoNotDisturb = 3
    inactive = 4
    meeting = 5
    OutOfOffice = 6
    pending = 7
    presenting = 8
    unknown = 9
