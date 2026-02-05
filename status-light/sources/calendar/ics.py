"""Status-Light
(c) 2020-2025 Nick Warner
https://github.com/portableprogrammer/Status-Light/

ICS Calendar Source
"""

# Standard imports
import os
from datetime import datetime, timedelta, timezone
import logging
import urllib.request

# 3rd-party imports
import icalendar
import recurring_ical_events

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

    # Cached calendar object
    _calendar: icalendar.Calendar | None = None

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

            # Invalidate cached calendar object
            self._calendar = None

            logger.debug('Successfully cached ICS file to: %s', cache_path)
            return True

        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Error fetching ICS file: %s', ex)
            logger.exception(ex)
            return False

    def _load_calendar(self) -> icalendar.Calendar | None:
        """Loads and parses the cached ICS file.

        Returns the calendar object or None on error."""
        if self._calendar is not None:
            return self._calendar

        cache_path = self._get_cache_path()
        try:
            with open(cache_path, 'rb') as f:
                self._calendar = icalendar.Calendar.from_ical(f.read())
            return self._calendar
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('Error loading ICS file: %s', ex)
            return None

    def _get_event_status(self, event: icalendar.Event) -> enum.Status:
        """Determines the Status-Light status for a single iCal event.

        RFC 5545 compliant mapping based on TRANSP and STATUS properties:
        - TRANSP=TRANSPARENT → FREE (event doesn't block time)
        - STATUS=CANCELLED → FREE (event was cancelled)
        - STATUS=TENTATIVE → TENTATIVE (maps to BUSY-TENTATIVE in RFC terms)
        - STATUS=CONFIRMED or None → BUSY (default blocking event)
        """
        summary = str(event.get('SUMMARY', 'Untitled'))

        # Transparent events don't block time (e.g., all-day reminders)
        transp = str(event.get('TRANSP', 'OPAQUE')).upper()
        if transp == 'TRANSPARENT':
            logger.debug('Event "%s" is transparent, treating as FREE', summary)
            return enum.Status.FREE

        # Check the STATUS property
        status = event.get('STATUS')
        status_str = str(status).upper() if status else None

        if status_str == 'CANCELLED':
            logger.debug('Event "%s" is cancelled, treating as FREE', summary)
            return enum.Status.FREE

        if status_str == 'TENTATIVE':
            logger.debug('Event "%s" is tentative, treating as TENTATIVE', summary)
            return enum.Status.TENTATIVE

        # CONFIRMED or no status = BUSY (default per RFC 5545)
        logger.debug('Event "%s" is confirmed/opaque, treating as BUSY', summary)
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

            # Load the calendar
            calendar = self._load_calendar()
            if calendar is None:
                return enum.Status.UNKNOWN

            # Get events within the lookahead window using timezone-aware datetimes
            # recurring-ical-events handles timezone conversion correctly
            local_tz = datetime.now().astimezone().tzinfo
            start_time = datetime.now(local_tz)
            end_time = start_time + timedelta(minutes=self.lookahead)

            logger.debug('Checking for events between %s and %s',
                        start_time.strftime('%I:%M %p %Z'),
                        end_time.strftime('%I:%M %p %Z'))

            # Use recurring-ical-events to expand recurring events and filter by time
            calendar_events = recurring_ical_events.of(calendar).between(start_time, end_time)

            if not calendar_events:
                logger.debug('No events in lookahead window')
                return enum.Status.FREE

            logger.debug('Found %d event(s) in lookahead window', len(calendar_events))

            # Determine the "busiest" status from all events
            # Precedence: BUSY > TENTATIVE > FREE
            has_tentative = False

            for event in calendar_events:
                dtstart = event.get('DTSTART')
                dtend = event.get('DTEND')
                summary = str(event.get('SUMMARY', 'Untitled'))
                transp = str(event.get('TRANSP', 'OPAQUE'))
                status = str(event.get('STATUS', ''))

                # Convert to local timezone for logging
                start_dt = dtstart.dt if dtstart else None
                end_dt = dtend.dt if dtend else start_dt
                if hasattr(start_dt, 'astimezone'):
                    start_local = start_dt.astimezone(local_tz)
                    end_local = end_dt.astimezone(local_tz) if hasattr(end_dt, 'astimezone') else end_dt
                else:
                    start_local = start_dt
                    end_local = end_dt

                logger.debug('Event: %s (%s - %s, transp=%s, status=%s)',
                            summary,
                            start_local.strftime('%I:%M %p') if start_local else '?',
                            end_local.strftime('%I:%M %p') if end_local else '?',
                            transp, status)

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
