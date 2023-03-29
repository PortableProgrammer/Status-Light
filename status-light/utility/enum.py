"""Status-Light
(c) 2020-2023 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Enumeration Definition
"""

# Standard imports
import enum


class StatusSource(enum.IntEnum):
    """Status Sources"""
    UNKNOWN = 0

    WEBEX = enum.auto()
    OFFICE365 = enum.auto()
    # 47 - Add Google support
    GOOGLE = enum.auto()
    # 48 - Add Slack suport
    SLACK = enum.auto()

    def _missing(self, value):
        return self.UNKNOWN


class Status(enum.IntEnum):
    """User statuses"""
    UNKNOWN = 0

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

    def _missing_(self, value):
        return self.UNKNOWN


class Color(enum.StrEnum):
    """Default Colors"""
    UNKNOWN = 'xxxxxx'

    RED = 'ff0000'
    YELLOW = 'ffff00'
    ORANGE = 'ff9000'
    GREEN = '00ff00'
    BLUE = '0000ff'

    def _missing_(self, value):
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

    def _missing(self, value):
        return self.UNKNOWN


class LogLevel(enum.IntEnum):
    """Log Levels"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10

    NOTSET = 0

    def _missing(self, value):
        return self.NOTSET
