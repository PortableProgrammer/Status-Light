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

    def get_status(self):
        """Retrieves the current status of the Tuya device.
        May return an error if the device is unavailable."""
        return tuyaface.status(self.device)

    def set_status(self, mode: enum.TuyaMode = enum.TuyaMode.WHITE,
                   color: str = enum.Color.WHITE.value, brightness: int = 128) -> bool:
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
            '2': mode.value
        }

        return_vaue = self._set_status(dps)
        return return_vaue

    def _set_status(self, dps: dict, retry: int = 5):
        """Internal Helper Method for `set_status`"""
        # We sometimes get a connection reset, or other errors, so let's retry after a second
        count = 0
        status = False
        while (status is False and count < retry):
            try:
                status = tuyaface.set_status(self.device, dps)
            except (SystemExit, KeyboardInterrupt):
                count = retry  # Break the loop
            except Exception as ex:  # pylint: disable=broad-except
                logger.warning('Exception sending to Tuya device, will retry %s more times: %s',
                               (retry - count), ex)
                count = count + 1
                time.sleep(1)

        # Still some strangeness; reusing the built-in connection in the "tuyaface" key
        #   causes a broken pipe error.
        #   Remove the "tuyaface" key to force a new connection
        self.device.pop('tuyaface')
        return status
