# https://github.com/portableprogrammer/Status-Light/

import tuyaface
from tuyaface import const as tf
import os
import time
from datetime import datetime

class TuyaLight:
    device = ''
    RED = "{ '1': 1, "
    YELLOW = ''
    ORANGE = ''
    GREEN = ''
    BLUE = ''
    WHITE = ''
    currentState = ""

    def on(self):
        tuyaface.set_state(self.device, True)

    def off(self):
        tuyaface.set_state(self.device, False)

    def transitionTo(self, toState):
        tuyaface.set_status(self.device, toState)

    def getStatus(self):
        return tuyaface.status(self.device)
