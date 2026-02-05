"""Status-Light
(c) 2020-2025 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Virtual Light Target for testing
"""

import logging

from utility import enum

logger = logging.getLogger(__name__)


class VirtualLight:
    """Virtual light target that logs status changes for testing."""
    _power: bool = False
    _mode: str = 'white'
    _color: str = 'ffffff'
    _brightness: int = 128

    def on(self):
        """Turns on the light."""
        logger.info('[Virtual] Light ON')
        self._power = True
        return True

    def off(self):
        """Turns off the light."""
        logger.info('[Virtual] Light OFF')
        self._power = False
        return True

    def get_status(self):
        """Retrieves the current status of the virtual device."""
        logger.info('[Virtual] Status: power=%s, mode=%s, color=%s, brightness=%s',
                    self._power, self._mode, self._color, self._brightness)
        return {'power': self._power, 'mode': self._mode,
                'color': self._color, 'brightness': self._brightness}

    def set_status(self, mode: enum.TuyaMode = enum.TuyaMode.WHITE,
                   color: str = enum.Color.WHITE.value,
                   brightness: int = 128) -> bool:
        """Sets the virtual light status.

        `mode`: `white`, `colour`
        `color`: A hex-formatted RGB color (e.g. `rrggbb`)
        `brightness`: An `int` between 0 and 255 inclusive
        """
        self._power = True
        self._mode = mode.value
        self._color = color
        self._brightness = brightness
        logger.info('[Virtual] set_status(mode=%s, color=%s, brightness=%s)',
                    mode.value, color, brightness)
        return True
