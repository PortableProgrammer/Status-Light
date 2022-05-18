"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Enumeration Definition
"""

# Standard imports
import enum

class Status(enum.Enum):
    unknown = 0

    # Collaboration (Webex, Slack)
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

    def _missing_(self, value): # pylint: disable=arguments-differ
        return self.unknown

class Color(enum.Enum):
    unknown = 'xxxxxx'

    red = 'ff0000'
    yellow = 'ffff00'
    orange = 'ff9000'
    green = '00ff00'
    blue = '0000f'

    def _missing_(self, value): # pylint: disable=arguments-differ
        return self.unknown

class StatusSource(enum.Enum):
    unknown = 0

    webex = 1
    office365 = 2
    # 47 - Add Google support
    google = 3
    # 48 - Add Slack suport
    slack = 4

    def _missing(self, value): # pylint: disable=unused-argument
        return self.unknown
