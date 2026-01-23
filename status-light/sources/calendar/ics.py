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

    def _get_event_status(self, event) -> enum.Status:
        """Determines the Status-Light status for a single iCal event.

        RFC 5545 compliant mapping based on TRANSP and STATUS properties:
        - TRANSP=TRANSPARENT → FREE (event doesn't block time)
        - STATUS=CANCELLED → FREE (event was cancelled)
        - STATUS=TENTATIVE → TENTATIVE (maps to BUSY-TENTATIVE in RFC terms)
        - STATUS=CONFIRMED or None → BUSY (default blocking event)
        """
        # Transparent events don't block time (e.g., all-day reminders)
        if event.transparent:
            logger.debug('Event "%s" is transparent, treating as FREE', event.summary)
            return enum.Status.FREE

        # Check the STATUS property
        status = event.status.upper() if event.status else None

        if status == 'CANCELLED':
            logger.debug('Event "%s" is cancelled, treating as FREE', event.summary)
            return enum.Status.FREE

        if status == 'TENTATIVE':
            logger.debug('Event "%s" is tentative, treating as TENTATIVE', event.summary)
            return enum.Status.TENTATIVE

        # CONFIRMED or no status = BUSY (default per RFC 5545)
        logger.debug('Event "%s" is confirmed/opaque, treating as BUSY', event.summary)
        return enum.Status.BUSY

    def get_current_status(self) -> enum.Status:
        """Retrieves the ICS calendar status within the lookahead period.

        RFC 5545 compliant behavior:
        - Returns BUSY if any confirmed opaque events exist
        - Returns TENTATIVE if only tentative events exist
        - Returns FREE if no blocking events exist
        - Returns UNKNOWN on error

        Status precedence: BUSY > TENTATIVE > FREE
        """
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

            if not calendar_events or len(calendar_events) == 0:
                logger.debug('No events in lookahead window')
                return enum.Status.FREE

            logger.debug('Found %d event(s) in lookahead window', len(calendar_events))

            # Determine the "busiest" status from all events
            # Precedence: BUSY > TENTATIVE > FREE
            has_tentative = False

            for event in calendar_events:
                logger.debug('Event: %s (%s - %s, transparent=%s, status=%s)',
                            event.summary, event.start, event.end,
                            event.transparent, event.status)

                event_status = self._get_event_status(event)

                if event_status == enum.Status.BUSY:
                    # BUSY takes precedence, return immediately
                    return enum.Status.BUSY

                if event_status == enum.Status.TENTATIVE:
                    has_tentative = True
                # FREE events don't affect the result

            # If we had any tentative events (but no busy), return TENTATIVE
            if has_tentative:
                return enum.Status.TENTATIVE

            # All events were transparent or cancelled
            return enum.Status.FREE

        except (SystemExit, KeyboardInterrupt):
            return enum.Status.UNKNOWN
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Exception while getting ICS status: %s', ex)
            logger.exception(ex)
            return enum.Status.UNKNOWN
