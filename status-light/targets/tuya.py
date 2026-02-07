"""Status-Light
(c) 2020-2026 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Tuya Target
"""

# Standard imports
import time
import logging

# 3rd-party imports
import tuyaface

# Project imports
from targets.base import LightTarget

logger = logging.getLogger(__name__)


class TuyaLight(LightTarget):
    """Represents a Tuya device, utilizing `tuyaface` for connections.

    Implements the LightTarget interface for Tuya-compatible RGB bulbs.
    Always uses COLOR mode internally (not white temperature mode).
    """
    device: dict

    def set_color(self, color: str, brightness: int) -> bool:
        """Set light to specified color and brightness.

        Args:
            color: 6-character hex RGB color (e.g., 'ff0000' for red)
            brightness: Brightness percentage 0-100

        Returns:
            True if successful, False otherwise

        Note:
            Tuya devices require specific DPS (Data Point) format. This method
            automatically converts the percentage brightness to Tuya's 0-255 scale,
            converts the hex color to Tuya's expected format, and locks the device
            to COLOR mode.
        """
        # Validate inputs using base class helpers
        if not self.validate_color(color):
            logger.warning('Invalid color format: %s (expected 6-char hex)', color)
            return False

        if not self.validate_brightness(brightness):
            logger.warning('Invalid brightness: %s (expected 0-100 percentage)', brightness)
            return False

        # Convert percentage (0-100) to Tuya's device scale (0-255)
        # Note: Tuya devices have a minimum usable threshold around 32-64
        device_brightness = int(brightness * 255 / 100)

        # Tuya DPS (Data Points):
        # 1: Power, bool
        # 2: Mode, 'white' or 'colour'
        # 3: Brightness, int 0-255 (lowest usable threshold is 32-64)
        # 5: Color, 'rrggbb0000ffff' (RGB + HSV suffix required by device)

        # Convert simple hex RGB to Tuya's DPS format
        if not color.endswith('0000ffff'):
            color = color + '0000ffff'

        # Command order matters: Power → Brightness → Color → Mode
        dps: dict = {
            '1': True,               # Power on
            '3': device_brightness,  # Set brightness (converted to 0-255)
            '5': color,              # Set color (with Tuya suffix)
            '2': 'colour'            # Lock to COLOR mode (not white temperature)
        }

        return self._set_dps(dps)

    def turn_off(self) -> bool:
        """Turn the light completely off.

        Returns:
            True if successful, False otherwise
        """
        return self._set_dps({'1': False})

    def _set_dps(self, dps: dict, retry: int = 5) -> bool:
        """Internal helper method for sending DPS commands to Tuya device.

        Args:
            dps: Dictionary of Data Point values to set
            retry: Number of retry attempts on failure (default: 5)

        Returns:
            True if successful, False otherwise

        Note:
            Implements retry logic with 1-second delays between attempts.
            Clears the tuyaface connection cache after each attempt to avoid
            broken pipe errors.
        """
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
