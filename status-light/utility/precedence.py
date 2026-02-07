"""Status-Light
(c) 2020-2026 Nick Warner
https://github.com/portableprogrammer/Status-Light/

Status Precedence Selection Logic
"""

# Standard imports
import logging

# Project imports
from utility import enum

logger: logging.Logger = logging.getLogger(__name__)


def select_status(
    collaboration_statuses: dict[enum.StatusSource, enum.Status],
    calendar_statuses: dict[enum.StatusSource, enum.Status],
    off_status: list[enum.Status],
    available_status: list[enum.Status]
) -> tuple[enum.Status, enum.StatusSource]:
    """Selects the winning status from multiple collaboration and calendar sources.

    Applies a hierarchical precedence algorithm:
    1. Collaboration sources (Webex, Slack) take precedence over Calendar sources
    2. Exception: Calendar overrides when collaboration is UNKNOWN or in off_status
       AND at least one calendar source has events (not in off_status)
    3. Within Collaboration: Webex > Slack
    4. Within Calendar: Office365 > Google > ICS

    Args:
        collaboration_statuses: Dictionary mapping StatusSource to Status for
            collaboration sources (e.g., {StatusSource.WEBEX: Status.MEETING})
        calendar_statuses: Dictionary mapping StatusSource to Status for
            calendar sources (e.g., {StatusSource.OFFICE365: Status.BUSY})
        off_status: List of Status values considered "off" (e.g., [Status.INACTIVE])
        available_status: List of Status values considered "available"
            (e.g., [Status.ACTIVE, Status.FREE])

    Returns:
        Tuple of (winning_status, winning_source) where:
        - winning_status: The selected Status enum value
        - winning_source: The StatusSource enum indicating which source won
        Returns (Status.UNKNOWN, StatusSource.UNKNOWN) if no valid status found

    Examples:
        >>> # Webex takes precedence over Slack
        >>> select_status(
        ...     {StatusSource.WEBEX: Status.MEETING, StatusSource.SLACK: Status.ACTIVE},
        ...     {},
        ...     [Status.INACTIVE],
        ...     [Status.ACTIVE]
        ... )
        (Status.MEETING, StatusSource.WEBEX)

        >>> # Calendar overrides when collaboration is available and calendar is busy
        >>> select_status(
        ...     {StatusSource.WEBEX: Status.ACTIVE},
        ...     {StatusSource.OFFICE365: Status.BUSY},
        ...     [Status.INACTIVE],
        ...     [Status.ACTIVE]
        ... )
        (Status.BUSY, StatusSource.OFFICE365)
    """
    # Log input sources for debugging
    if collaboration_statuses:
        collab_log = ', '.join(f'{src.name.lower()}={status.name.lower()}'
                               for src, status in collaboration_statuses.items())
        logger.debug('Collaboration sources: %s', collab_log)
    else:
        logger.debug('Collaboration sources: none')

    if calendar_statuses:
        calendar_log = ', '.join(f'{src.name.lower()}={status.name.lower()}'
                                 for src, status in calendar_statuses.items())
        logger.debug('Calendar sources: %s', calendar_log)
    else:
        logger.debug('Calendar sources: none')

    # Phase 1: Select collaboration status
    # Check Webex first (highest priority)
    current_status = collaboration_statuses.get(enum.StatusSource.WEBEX, enum.Status.UNKNOWN)
    winning_source = enum.StatusSource.WEBEX

    # If Webex is UNKNOWN or in off_status, fallback to Slack
    if (current_status == enum.Status.UNKNOWN or current_status in off_status):
        slack_status = collaboration_statuses.get(enum.StatusSource.SLACK, enum.Status.UNKNOWN)
        if slack_status != enum.Status.UNKNOWN:
            logger.debug('Using slack_status: %s', slack_status.name.lower())
            current_status = slack_status
            winning_source = enum.StatusSource.SLACK
        elif current_status != enum.Status.UNKNOWN:
            # Webex returned an off_status value, using it
            logger.debug('Using webex_status: %s (off_status)', current_status.name.lower())
    else:
        # Webex has a valid collaboration status, using it
        logger.debug('Using webex_status: %s', current_status.name.lower())

    # Phase 2: Check calendar override condition
    # Calendar overrides if:
    # - Current status is in available_status OR off_status
    # - At least one calendar source is NOT in off_status (has events)
    if (current_status in available_status or current_status in off_status):
        # Check if any calendar source has events
        office_status = calendar_statuses.get(enum.StatusSource.OFFICE365, enum.Status.UNKNOWN)
        google_status = calendar_statuses.get(enum.StatusSource.GOOGLE, enum.Status.UNKNOWN)
        ics_status = calendar_statuses.get(enum.StatusSource.ICS, enum.Status.UNKNOWN)

        if (office_status not in off_status or
            google_status not in off_status or
            ics_status not in off_status):

            logger.debug('Using calendar-based status (overriding collaboration status: %s)',
                        current_status.name.lower())

            # Phase 3: Select calendar status in priority order
            # Office365 > Google > ICS
            if office_status != enum.Status.UNKNOWN:
                logger.debug('Using office_status: %s', office_status.name.lower())
                current_status = office_status
                winning_source = enum.StatusSource.OFFICE365
            elif google_status != enum.Status.UNKNOWN:
                logger.debug('Using google_status: %s', google_status.name.lower())
                current_status = google_status
                winning_source = enum.StatusSource.GOOGLE
            else:
                # Use ICS as final fallback even if UNKNOWN
                logger.debug('Using ics_status: %s', ics_status.name.lower())
                current_status = ics_status
                winning_source = enum.StatusSource.ICS
        else:
            logger.debug('Calendar sources all off, keeping collaboration status: %s',
                        current_status.name.lower())
    else:
        logger.debug('Collaboration status %s not overrideable, keeping it',
                    current_status.name.lower())

    # Log final decision
    logger.debug('Selected status: %s from source: %s',
                current_status.name.lower(), winning_source.name.lower())

    # Return the winning status and its source
    return (current_status, winning_source)
