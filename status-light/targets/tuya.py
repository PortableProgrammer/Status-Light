# https://github.com/portableprogrammer/Status-Light/

# Standard imports
import time
import logging

# 3rd-party imports
import tuyaface

# Project imports
from utility import const
from utility import env

logger = logging.getLogger(__name__)

class TuyaLight:
    device = ''

    def turn_on(self):
        return self.set_single_state(1, True)

    def turn_off(self):
        return self.set_single_state(1, False)

    def set_single_state(self, index, value, retry: int = 5):
        # We sometimes get a connection reset, or other errors, so let's retry after a second
        count = 0
        status = None
        while (status is None and count < retry):
            try:
                status = tuyaface.set_status(self.device, {index: value})
            except (SystemExit, KeyboardInterrupt):
                count = retry # Break the loop
            except BaseException as exc:
                logger.warning('Exception during setSingleState: %s', exc)
                count = count + 1
                time.sleep(1)
        return status

    def set_state(self, mode = 'white', color = 'ffffff', brightness: int = 128):
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

        # The code below is the probable cause of #2.
        # Upgrading the tuya client via #36 might help fix it.
        self.turn_on()
        self.set_single_state(3, brightness)
        self.set_single_state(5, color)
        self.set_single_state(2, mode)


    def get_status(self):
        return tuyaface.status(self.device)

    def transition_status(self, status: const.Status, environment: env.Environment):
        #43: Coalesce the statuses and only execute setState once.
        # This will still allow a single status to be in more than one list,
        # but will not cause the light to rapidly switch between states.
        color = None

        if status in environment.available_status:
            color = environment.available_color

        if status in environment.scheduled_status:
            color = environment.scheduled_color

        if status in environment.busy_status:
            color = environment.busy_color

        if color is not None:
            self.set_state('colour', color, environment.tuya_brightness)
        # OffStatus has the lowest priority, so only check it if none of the others are valid
        elif status in environment.off_status:
            self.turn_off()
        # In the case that we made it here without a valid state,
        # just turn the light off and warn about it
        else:
            logger.warning('transition_status called with an invalid status: %s',status)
            self.turn_off()
