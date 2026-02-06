"""Status-Light
(c) 2020-2026 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Utility Functions
"""

# Standard imports
import logging
from datetime import datetime, time
from enum import EnumType
import re
import os


# Project imports
from utility import enum

logger: logging.Logger = logging.getLogger(__name__)

# 41: Replace decoractor with utility function


def try_parse_int(value, default: int, base: int = 10) -> int:
    """For a given value and base, attempts to convert that value into an integer.

    Value is, presumably, a string, though it can be any type that the int() function accepts:
    https://docs.python.org/3/library/functions.html#int
    """
    # If we received None or an empty string, just return the default
    if value in [None, '']:
        return default

    try:
        return int(value, base)
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception encountered during try_parse_int: %s, using default: %s',
                       ex, default)
        return default

# 45: Add support for active hours


def try_parse_datetime(value: str, default: datetime, format: str = "%H:%M:%S") -> datetime: # pylint: disable=redefined-builtin
    """For a given string value and format, attempts to convert that value into a datetime."""
    # If we received None or an empty string, just return the default
    if value in [None, '']:
        return default

    try:
        return datetime.strptime(value, format)
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception while parsing datetime: %s, using default: %s',
                       ex, default)
        return default


def is_active_hours(active_days: list[enum.Weekday], active_hours_start: time,
                    active_hours_end: time) -> bool:
    """For a given set of active days and start and end times,
    determine if `datetime.now()` is within the active period."""
    try:
        current_time = datetime.now()
        # First, is the current weekday within the active_days list?
        if current_time.weekday() not in active_days:
            return False

        # Now determine if the current time between the start and end times
        if current_time.time() < active_hours_start or current_time.time() > active_hours_end:
            return False

        # Otherwise, we're within an active period
        return True
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception while checking for active hours: %s', ex)
        return False


def parse_color(color_string: str, default: str) -> str:
    """Given a string or Color enum value, attempts to parse the string into a hex color."""
    temp_color = default
    if color_string in [None, '']:
        return temp_color

    try:
        # We accept both a set of constants [red, green, blue, yellow, orange]
        # or a standard hex RGB (rrggbb) input
        if not re.match('^[0-9A-Fa-f]{6}$', color_string) is None:
            temp_color = color_string
        else:
            # _parse_enum returns an enum, get the value (the actual hex color value)
            temp_color = enum.Color(parse_enum(
                color_string, enum.Color, "parse_color", enum.Color(default))).value
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception while parsing color: %s, using default: %s',
                       ex, default)
        temp_color = default
    return temp_color


def parse_enum(value_string: str, value_enum: EnumType, description: str, default) -> EnumType:
    """Given a string and an enumeration, attempts to parse the string into enums."""
    temp_value: EnumType = default
    if value_string in [None, '']:
        return temp_value

    try:
        temp_value = value_enum[value_string.upper().strip()]
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception encountered for %s: %s', description, ex)
        temp_value = default
    return temp_value


def parse_enum_list(value_string: str, value_enum: EnumType,
                    description: str, default) -> list[EnumType]:
    """Given a string and an enumeration, attempts to parse the string into enums."""
    temp_value: list[EnumType] = default
    if value_string in [None, '']:
        return temp_value

    try:
        temp_value = list(parse_enum(value, value_enum, description, default)
                          for value in value_string.split(','))
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception encountered for %s: %s', description, ex)
        temp_value = default
    return temp_value

# 66 - Support Slack custom statuses


def parse_str_array(value_string: str | list[str], default: list[str],
                    delimiter: str = ',', casefold: bool = False) -> list[str]:
    """Given a string containing an array of strings, attempts to parse the string into an array.
    Pass casefold=True to build an array ready for case-insensitive comparison."""
    temp_value = default
    if value_string in [None, '']:
        value_string = temp_value

    try:
        # Ensure that we return a true list, since the incoming string
        # might have a single element only.
        if not isinstance(value_string, list):
            temp_value = []
            for value in value_string.split(delimiter):
                if casefold:
                    value = value.casefold()
                temp_value.append(value)
        else:
            temp_value = []
            if casefold:
                for value in value_string:
                    temp_value.append(value.casefold())

    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('Exception while parsing a string array: %s', ex)
        temp_value = default
    return temp_value

# 30 - Docker Secrets


def get_env_or_secret(variable: str, default: str, treat_empty_as_none: bool = True) -> str:
    """Given a variable name, returns the Environment or File variant of the variable.
    If both are None, returns default.

    For a given variable name, e.g. O365_APPSECRET, this method will check for both
    the standard environment variable (O365_APPSECRET) as well as the _FILE variant
    (O365_APPSECRET_FILE).

    Precedence is given to the standard environment variable, and the _FILE variant
    is only checked if the standard variant is nonexistent or None.
    If treat_empty_as_none is true (which is the default), this method will also treat
    empty strings returned from either variant as None, and trigger the next check
    or return the default.

    Note that this method does not attempt to parse or validate the value in variable;
    it simply returns the raw string found, if any.
    """
    value = default
    try:
        # First, check the standard variant
        value = os.environ.get(variable, None)

        # If this value is None or an empty string,
        if value is None or (treat_empty_as_none and value == ''):
            # Check the _FILE variant
            secret_filename = os.environ.get(variable + '_FILE', None)
            if secret_filename is not None and (treat_empty_as_none and value != ''):
                value = _read_file(secret_filename)
        else:
            # Strip the whitespace
            value = value.strip()
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning(
            'Exception encountered getting value for %s: %s', variable, ex)
        value = default

    # Finally, if the value is nonexistent or empty, just return the default
    if value is None or (treat_empty_as_none and value == ''):
        value = default

    return value


def _read_file(file: str, strip: bool = True) -> str:
    """Read, and optionally strip spaces from, a file."""
    secret = ''

    if not os.access(file, os.F_OK):
        return secret
    else:
        try:
            with open(file) as file_contents:  # pylint: disable=unspecified-encoding
                secret = file_contents.read()
                if strip:
                    secret = secret.strip()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Exception encountered reading file: %s', ex)
            secret = ''
    return secret
