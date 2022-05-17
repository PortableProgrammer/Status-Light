# Standard imports
import logging

logger = logging.getLogger(__name__)

# 41: Replace decoractor with utility function
def try_parse_int(value, base = 10, default = None):
    """For a given value and base, attempts to convert that value into an integer.

    Value is, presumably, a string, though it can be any type that the int() function accepts:
    https://docs.python.org/3/library/fuctnions.html#int
    """
    try:
        return int(value, base)
    except BaseException as ex:
        logger.warning('Exception encountered during try_parse_int: %s, using default: %s',
            ex, default)
        return default
