import enum

class Status(enum.Enum):
    unknown = 0

    # Webex
    active = 1
    call = 2
    donotdisturb = 3
    inactive = 4
    meeting = 5
    pending = 6
    presenting = 7

    #Office
    free = 8
    tentative = 9
    busy = 10
    outofoffice = 11
    workingelsewhere = 12

    def _missing_(self, value):
        return self.unknown

class Color(enum.Enum):
    unknown = 'xxxxxx'

    Red = 'ff0000'
    Yellow = 'ffff00'
    Orange = 'ff9000'
    Green = '00ff00'
    Blue = '0000f'

    def _missing_(self, value):
        return self.unknown

