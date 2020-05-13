import enum

class Status(enum.Enum):
    unknown = 0

    # Webex
    active = 1
    call = 2
    DoNotDisturb = 3
    inactive = 4
    meeting = 5
    OutOfOffice = 6
    pending = 7
    presenting = 8

    #Office
    free = 9
    busy = 10
    tentative = 11

OFF = [Status.inactive, Status.OutOfOffice, Status.unknown, Status.free]
GREEN = [Status.active]
ORANGE = [Status.busy, Status.tentative]
RED = [Status.call, Status.DoNotDisturb, Status.meeting, Status.presenting]
