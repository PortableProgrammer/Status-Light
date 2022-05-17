import enum

class Status(enum.Enum):
    unknown = 0

    # Collaboration (Webex)
    active = 1
    call = 2
    donotdisturb = 3
    inactive = 4
    meeting = 5
    pending = 6
    presenting = 7

    # Calendars (Office, Google)
    free = 8
    tentative = 9
    busy = 10
    outofoffice = 11
    workingelsewhere = 12

    def _missing_(self, value):
        return self.unknown

class Color(enum.Enum):
    unknown = 'xxxxxx'

    red = 'ff0000'
    yellow = 'ffff00'
    orange = 'ff9000'
    green = '00ff00'
    blue = '0000f'

    def _missing_(self, value):
        return self.unknown

class StatusSource(enum.Enum):
    unknown = 0

    webex = 1
    office365 = 2
    #47: Add Google support
    google = 3

    def _missing(self, value):
        return self.unknown