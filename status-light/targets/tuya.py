"""Status-Light
(c) 2020-2023 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Tuya Target
"""

# Standard imports
import time
import logging

# 3rd-party imports
import tuyaface

# Project imports
from utility import enum
from utility import env

logger = logging.getLogger(__name__)


class TuyaLight:
    """Represents a Tuya device, utilizing `tuyaface` for connections."""
    device: dict

    def on(self):  # pylint: disable=invalid-name
        """Turns on the light."""
        return self._set_status({'1': True})

    def off(self):
        """Turns off the light."""
        return self._set_status({'1': False})

    def set_status(self, mode='white', color='ffffff', brightness: int = 128):
        """Sends a full command to the Tuya device

        `mode`: `white`, `colour`
        `color`: A hex-formatted RGB color (e.g. `rrggbb`)
        `brightness`: An `int` between 0 and 255 inclusive, though the lowest usable threshold is 32
        """
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

        dps: dict = {
            '1': True,
            '3': brightness,
            '5': color,
            '2': mode
        }

        return_vaue = self._set_status(dps)
        return return_vaue

    def _set_status(self, dps: dict, retry: int = 5):
        """Internal helper for `set_status`"""
        # We sometimes get a connection reset, or other errors, so let's retry after a second
        count = 0
        status = False
        while (status is False and count < retry):
            try:
                status = tuyaface.set_status(self.device, dps)
            except (SystemExit, KeyboardInterrupt):
                count = retry  # Break the loop
            except Exception as ex:  # pylint: disable=broad-except
                logger.warning('Exception sending to Tuya device: %s', ex)
                count = count + 1
                time.sleep(1)

        # Still some strangeness; reusing the built-in connection in the "tuyaface" key
        #   causes a broken pipe error.
        #   Remove the "tuyaface" key to force a new connection
        self.device.pop('tuyaface')
        return status

    def get_status(self):
        """Retrieves the current status of the Tuya device.
        May return an error if the device is unavailable."""
        return tuyaface.status(self.device)

    def transition_status(self, status: enum.Status, environment: env.Environment) -> bool:
        """Given a `Status` and `Environment`, determine which color is appropriate, and execute
        the `set_status` call to transition to that color.
        """
        # 43: Coalesce the statuses and only execute setState once.
        # This will still allow a single status to be in more than one list,
        # but will not cause the light to rapidly switch between states.
        color = None
        return_value = False

        if status in environment.available_status:
            color = environment.available_color

        if status in environment.scheduled_status:
            color = environment.scheduled_color

        if status in environment.busy_status:
            color = environment.busy_color

        if color is not None:
            return_value = self.set_status(
                'colour', color, environment.tuya_brightness)
        # OffStatus has the lowest priority, so only check it if none of the others are valid
        elif status in environment.off_status:
            return_value = self.off()
        # In the case that we made it here without a valid state,
        # just turn the light off and warn about it
        # 74: Log enums as names, not values
        else:
            logger.warning('Called with an invalid status: %s',
                           status.name.lower())
            return_value = self.off()

        return return_value
