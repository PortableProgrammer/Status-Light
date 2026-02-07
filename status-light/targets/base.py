"""Status-Light
(c) 2020-2026 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Abstract Light Target Base Class
"""

# Standard imports
import re
from abc import ABC, abstractmethod


class LightTarget(ABC):
    """Abstract base class for light targets.

    Defines the interface that all light targets must implement.
    Status-Light uses a simple model: set a color with brightness, or turn off.
    """

    @abstractmethod
    def set_color(self, color: str, brightness: int) -> bool:
        """Set light to specified color and brightness.

        Args:
            color: 6-character hex RGB color (e.g., 'ff0000' for red)
            brightness: Brightness percentage 0-100 (0 effectively off, but
                use turn_off() for clarity)

        Returns:
            True if successful, False otherwise

        Note:
            Implementations should convert the percentage brightness to their device-specific
            format (e.g., Tuya uses 0-255, Hue uses 0-254, LIFX uses 0.0-1.0).
        """
        pass

    @abstractmethod
    def turn_off(self) -> bool:
        """Turn the light completely off.

        Returns:
            True if successful, False otherwise

        Note:
            This is preferred over set_color() with brightness=0 for clarity and
            to allow implementations to optimize for the off state.
        """
        pass

    def validate_color(self, color: str) -> bool:
        """Validate color format (6-character hex RGB).

        Args:
            color: String to validate as hex color

        Returns:
            True if color is valid 6-character hex, False otherwise

        Note:
            Implementations can override this for custom validation or
            to accept additional color formats.
        """
        return bool(re.match(r'^[0-9A-Fa-f]{6}$', color))

    def validate_brightness(self, brightness: int) -> bool:
        """Validate brightness percentage (0-100).

        Args:
            brightness: Integer percentage value to validate

        Returns:
            True if brightness is in valid range, False otherwise

        Note:
            Base class expects percentage (0-100). Implementations convert this to
            device-specific ranges. Override this method if you need different validation.
        """
        return 0 <= brightness <= 100
