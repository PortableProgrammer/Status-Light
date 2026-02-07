"""Status-Light
(c) 2020-2026 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Virtual Light Target for testing
"""

import logging

from targets.base import LightTarget

logger = logging.getLogger(__name__)


class VirtualLight(LightTarget):
    """Virtual light target that logs status changes for testing.

    Implements the LightTarget interface without requiring any physical hardware.
    Useful for development, testing, and demonstrations.
    """
    _power: bool = False
    _color: str = 'ffffff'
    _brightness: int = 128

    def set_color(self, color: str, brightness: int) -> bool:
        """Set virtual light to specified color and brightness.

        Args:
            color: 6-character hex RGB color (e.g., 'ff0000' for red)
            brightness: Brightness level 0-255

        Returns:
            Always returns True (virtual light cannot fail)
        """
        # Validate inputs using base class helpers
        if not self.validate_color(color):
            logger.warning('[Virtual] Invalid color format: %s (expected 6-char hex)', color)
            return False

        if not self.validate_brightness(brightness):
            logger.warning('[Virtual] Invalid brightness: %s (expected 0-255)', brightness)
            return False

        self._power = True
        self._color = color
        self._brightness = brightness
        logger.info('[Virtual] set_color(color=%s, brightness=%s)', color, brightness)
        return True

    def turn_off(self) -> bool:
        """Turn the virtual light off.

        Returns:
            Always returns True (virtual light cannot fail)
        """
        self._power = False
        logger.info('[Virtual] turn_off()')
        return True
