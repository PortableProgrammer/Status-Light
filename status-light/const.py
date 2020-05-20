import enum

class Status(enum.Enum):
    unknown = 0

    # Webex
    active = 1
    call = 2
    DoNotDisturb = 3
    inactive = 4
    meeting = 5
    pending = 6
    presenting = 7

    #Office
    free = 8
    tentative = 9
    busy = 10
    OutOfOffice = 11
    WorkingElsewhere = 12

OFF = [Status.inactive, Status.OutOfOffice, Status.unknown, Status.free]
GREEN = [Status.active]
ORANGE = [Status.busy, Status.tentative]
RED = [Status.call, Status.DoNotDisturb, Status.meeting, Status.presenting]
