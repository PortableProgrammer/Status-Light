# https://github.com/portableprogrammer/Status-Light/

import tuyaface
from tuyaface import const as tf
import os
import time
from datetime import datetime
import logging

# Project imports
import const
import env

logger = logging.getLogger(__name__)

class TuyaLight:
    device = ''

    def on(self):
        return self.setSingleState(1, True)

    def off(self):
        return self.setSingleState(1, False)

    def setSingleState(self, index, value, retry: int = 5):
        # We sometimes get a connection reset, or other errors, so let's retry after a second
        count = 0
        status = None
        while (status == None and count < retry):
            try:
                status = tuyaface.set_status(self.device, {index: value})
            except (SystemExit, KeyboardInterrupt):
                count = retry # Break the loop
            except BaseException as e:
                logger.warning('Exception during setSingleState: %s',e)
                count = count + 1
                time.sleep(1)
        return status

    def setState(self, mode = 'white', color = 'ffffff', brightness: int = 128):
        # DPS:
        # 1: Power, bool
        # 2: Mode, 'white' or 'colour'
        # 3: Brightness, int 0-255, but the lowest usable threshold is between 32 and 64
        # 5: Color, 'rrggbb0000ffff'

        # Ensure the color has all the bits we care about
        if not color.endswith('0000ffff'):
            color = color + '0000ffff'

        # Light must be on (so we'll do that first)
        # Brightness should be next
        # Color must be before Mode

        self.on()
        self.setSingleState(3, brightness)
        self.setSingleState(5, color)
        self.setSingleState(2, mode)


    def getStatus(self):
        return tuyaface.status(self.device)

    def transitionStatus(self, status: const.Status, environment: env.Environment):
        # Take the statii and determine what we care about most
        # White/Green/Off when available
        # Yellow/Orange when in a meeting (Calendar)
        # Red when on a Webex call/meeting or DnD (due to the way that Webex Teams handles status priorities) - This takes priority over calendar

        if status in environment.offStatus: 
            self.off()

        if status in environment.availableStatus:
            self.setState('colour', environment.availableColor, environment.tuyaBrightness)

        if status in environment.scheduledStatus:
            self.setState('colour', environment.scheduledColor, environment.tuyaBrightness)

        if status in environment.busyStatus: 
            self.setState('colour', environment.busyColor, environment.tuyaBrightness)
