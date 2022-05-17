# https://github.com/portableprogrammer/Status-Light/

import tuyaface
from tuyaface import const as tf
import os
import time
from datetime import datetime
import logging

# Project imports
from utility import const
from utility import env

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

        # The code below is the probable cause of #2. Upgrading the tuya client via #36 might help fix it.
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

        #43: Coalesce the statuses and only execute setState once. This will still allow a single status to be in more than one list, but will not cause the light to rapidly switch between states.
        color = None

        if status in environment.availableStatus:
            color = environment.availableColor

        if status in environment.scheduledStatus:
            color = environment.scheduledColor

        if status in environment.busyStatus: 
            color = environment.busyColor

        if color != None:
            self.setState('colour', color, environment.tuyaBrightness)
        # OffStatus has the lowest priority, so only check it if none of the others are valid
        elif status in environment.offStatus:
            self.off()
        # In the case that we made it here without a valid state, just turn the light off and warn about it
        else:
            logger.warning('transitionStatus called with an invalid status: %s',status)
            self.off()
