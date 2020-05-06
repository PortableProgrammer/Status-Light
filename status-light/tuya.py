# https://github.com/portableprogrammer/Status-Light/

import tuyaface
from tuyaface import const as tf
import os
import time
from datetime import datetime
import logging

# Project imports
import const

logger = logging.getLogger(__name__)

class TuyaLight:
    device = ''
    RED = 'ff00000000ffff'
    YELLOW = 'ffff000000ffff'
    ORANGE = 'ffa5000000ffff'
    GREEN = '00ff000000ffff'
    BLUE = '0000ff0000ffff'

    def on(self):
        return self.setSingleState(1, True)

    def off(self):
        return self.setSingleState(1, False)

    def setSingleState(self, index, value, retry: int = 5):
        # We sometimes get a connection reset, or other errors, so let's retry after a second
        count = 0
        while (True and count < retry):
            try:
                return tuyaface.set_status(self.device, {index: value})
                count = retry # Break the loop
            except BaseException as e:
                logger.warn('Exception during setSingleState:',e)
                count = count + 1
                time.sleep(1)

    def setState(self, mode = 'white', color = 'ffffff0000ffff', brightness: int = 128):
        # DPS:
        # 1: Power, bool
        # 2: Mode, 'white' or 'colour'
        # 3: Brightness, int 0-255
        # 5: Color, 'rrggbb0000ffff'

        # Light must be on (so we'll do that first)
        # Brightness can be set whenever (so we'll do that next)
        # Color must be before Mode
        self.on()
        self.setSingleState(3, brightness)
        self.setSingleState(5, color)
        self.setSingleState(2, mode)

        # NOTE: Ideally, we should be able to do something like the below, but it doesn't seem to work for my devices
        # tuyaface.set_status(self.device, {1: True, 2: mode, 3: brightness, 5: color})

    def getStatus(self):
        return tuyaface.status(self.device)

    def transitionStatus(self, status: const.Status):
        # Take the statii and determine what we care about most
        # White/Green/Off when available
        # Yellow/Orange when in a meeting (Calendar)
        # Red when on a Webex call/meeting or DnD (due to the way that Webex Teams handles status priorities) - This takes priority over calendar

        if status in const.OFF: 
            self.off()

        if status in const.GREEN:
            self.setState('colour', self.GREEN)

        if status in const.YELLOW:
            self.setState('colour', self.YELLOW)

        if status in const.RED: 
            self.setState('colour', self.RED)
