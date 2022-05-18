"""Status-Light
(c) 2020-2022 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Enumeration Definition
"""

# Standard imports
import enum

class StatusSource(enum.IntEnum):
    """Status Sources"""
    UNKNOWN = enum.auto()

    WEBEX = enum.auto()
    OFFICE365 = enum.auto()
    # 47 - Add Google support
    GOOGLE = enum.auto()
    # 48 - Add Slack suport
    SLACK = enum.auto()

    def _missing(self, value): # pylint: disable=unused-argument
        return self.UNKNOWN

class Status(enum.IntEnum):
    """User statuses"""
    UNKNOWN = enum.auto()

    # Collaboration (Webex, Slack)
    ACTIVE = enum.auto()
    CALL = enum.auto()
    DONOTDISTURB = enum.auto()
    INACTIVE = enum.auto()
    MEETING = enum.auto()
    PENDING = enum.auto()
    PRESENTING = enum.auto()

    # Calendars (Office, Google)
    FREE = enum.auto()
    TENTATIVE = enum.auto()
    BUSY = enum.auto()
    OUTOFOFFICE = enum.auto()
    WORKINGELSEWHERE = enum.auto()

    def _missing_(self, value): # pylint: disable=arguments-differ
        return self.UNKNOWN

class Color(enum.Enum):
    """Default Colors"""
    UNKNOWN = 'xxxxxx'

    RED = 'ff0000'
    YELLOW = 'ffff00'
    ORANGE = 'ff9000'
    GREEN = '00ff00'
    BLUE = '0000f'

    def _missing_(self, value): # pylint: disable=arguments-differ
        return self.UNKNOWN

class Weekday(enum.IntEnum):
    """Days of the week"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    UNKNOWN = 7

    def _missing(self, value): # pylint: disable=unused-argument
        return self.UNKNOWN

class LogLevel(enum.IntEnum):
    """Log Levels"""
    CRITICAL = enum.auto()
    ERROR = enum.auto()
    WARNING = enum.auto()
    INFO = enum.auto()
    DEBUG = enum.auto()

    UNKNOWN = enum.auto()

    def _missing(self, value): # pylint: disable=unused-argument
        return self.UNKNOWN
