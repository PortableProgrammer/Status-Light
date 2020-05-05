# https://github.com/portableprogrammer/Status-Light/

import tuyaface
from tuyaface import const as tf
import os
import time
from datetime import datetime

class TuyaLight:
    device = ''
    RED = 'ff00000000ffff'
    YELLOW = ''
    ORANGE = ''
    GREEN = '00ff000000ffff'
    BLUE = '0000ff0000ffff'
    currentState = ""

    def on(self):
        return tuyaface.set_state(self.device, True)

    def off(self):
        return tuyaface.set_state(self.device, False)

    def setSingleState(self, index, value):
        return tuyaface.set_status(self.device, {index: value})

    def transitionTo(self, toState):
        return tuyaface.set_status(self.device, toState)

    def getStatus(self):
        return tuyaface.status(self.device)
