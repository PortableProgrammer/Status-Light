"""Status-Light
(c) 2020-2025 Nick Warner
https://github.com/portableprogrammer/Status-Light/

ICS Calendar Source
"""

# Standard imports
import os
import os.path
from datetime import datetime, timedelta, timezone
import logging
import urllib.request

# 3rd-party imports
from icalevents.icalevents import events

# Project imports
from utility import enum

logger = logging.getLogger(__name__)


class Ics:
    """Handles ICS Calendar"""

    url: str = ''

    cacheStore: str = '~'
    cacheFile: str = 'status-light-ics-cache.ics'
    cacheLifetime: int = 30

    # 81 - Make calendar lookahead configurable
    lookahead: int = 5

    def _get_cache_path(self) -> str:
        """Returns the full path to the cache file."""
        return os.path.normpath(os.path.join(
            os.path.expanduser(self.cacheStore),
            self.cacheFile
        ))

    def _should_refresh_cache(self) -> bool:
        """Checks if the cache file is stale or missing.

        Returns True if the cache should be refreshed."""
        cache_path = self._get_cache_path()

        # If the file doesn't exist, we need to fetch
        if not os.path.exists(cache_path):
            logger.debug('Cache file does not exist: %s', cache_path)
            return True

        # Check if the file is older than the cache lifetime
        try:
            file_mtime = datetime.fromtimestamp(
                os.stat(cache_path).st_mtime, tz=timezone.utc)
            cache_expiry = datetime.now(timezone.utc) - timedelta(minutes=self.cacheLifetime)

            if file_mtime < cache_expiry:
                logger.debug('Cache file is stale (mtime: %s, expiry: %s)',
                            file_mtime, cache_expiry)
                return True

            logger.debug('Cache file is still valid (mtime: %s)', file_mtime)
            return False
        except OSError as ex:
            logger.warning('Error checking cache file: %s', ex)
            return True

    def _fetch_and_cache(self) -> bool:
        """Downloads the ICS file and saves it to the cache.

        Returns True on success, False on failure."""
        cache_path = self._get_cache_path()

        try:
            logger.debug('Fetching ICS from URL: %s', self.url)

            # Create cache directory if it doesn't exist
            cache_dir = os.path.dirname(cache_path)
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

            # Download the ICS file
            with urllib.request.urlopen(self.url, timeout=30) as response:
                ics_content = response.read()

            # Write to cache file
            with open(cache_path, 'wb') as cache_file:
                cache_file.write(ics_content)

            logger.debug('Successfully cached ICS file to: %s', cache_path)
            return True

        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Error fetching ICS file: %s', ex)
            logger.exception(ex)
            return False

    def get_current_status(self) -> enum.Status:
        """Retrieves the ICS calendar status within the lookahead period.

        Returns BUSY if there are events in the lookahead window,
        FREE if there are no events, or UNKNOWN on error."""
        try:
            # Refresh cache if needed
            if self._should_refresh_cache():
                if not self._fetch_and_cache():
                    # If fetch fails but we have an old cache, try to use it
                    cache_path = self._get_cache_path()
                    if not os.path.exists(cache_path):
                        logger.warning('No cached ICS file available')
                        return enum.Status.UNKNOWN
                    logger.warning('Using stale cache file due to fetch failure')

            cache_path = self._get_cache_path()

            # Get events within the lookahead window
            start_time = datetime.now(timezone.utc)
            end_time = start_time + timedelta(minutes=self.lookahead)

            logger.debug('Checking for events between %s and %s', start_time, end_time)

            # Use icalevents to parse the cached file
            calendar_events = events(file=cache_path, start=start_time, end=end_time)

            if calendar_events and len(calendar_events) > 0:
                logger.debug('Found %d event(s) in lookahead window', len(calendar_events))
                for event in calendar_events:
                    logger.debug('Event: %s (%s - %s)',
                                event.summary, event.start, event.end)
                return enum.Status.BUSY
            else:
                logger.debug('No events in lookahead window, assuming Free')
                return enum.Status.FREE

        except (SystemExit, KeyboardInterrupt):
            return enum.Status.UNKNOWN
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Exception while getting ICS status: %s', ex)
            logger.exception(ex)
            return enum.Status.UNKNOWN
