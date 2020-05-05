import enum

class Status(enum.Enum):
    active = 1
    call = 2
    DoNotDisturb = 3
    inactive = 4
    meeting = 5
    CalendarMeeting = 6
    OutOfOffice = 7
    pending = 8
    presenting = 9
    unknown = 10

OFF = [Status.inactive, Status.OutOfOffice, Status.unknown]
GREEN = [Status.active]
YELLOW = [Status.CalendarMeeting]
RED = [Status.call, Status.DoNotDisturb, Status.meeting, Status.presenting]
