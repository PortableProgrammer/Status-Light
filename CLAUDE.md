# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Status-Light monitors user status across collaboration platforms (Webex, Slack) and calendars (Office 365, Google Calendar) to display the "busiest" status on a Tuya RGB LED smart bulb. The application runs as a continuous polling loop inside a Docker container.

## Running the Application

**Local execution:**
```bash
python -u status-light/status-light.py
```

**Docker (preferred):**
```bash
docker run -e SOURCES=webex,office365 -e WEBEX_PERSONID=... portableprogrammer/status-light
```

**Build Docker image locally:**
```bash
docker build -f Dockerfiles/Dockerfile -t status-light .
```

There is no formal test suite, linter configuration, or build system. Development testing is done manually through Docker.

## Architecture

### Core Application Flow

`status-light/status-light.py` is the entry point containing the `StatusLight` class which:
1. Validates environment variables and initializes configured sources
2. Runs a continuous polling loop (configurable via `SLEEP_SECONDS`)
3. Queries each enabled source for current status
4. Applies status precedence rules to determine the "busiest" status
5. Updates the Tuya smart light color accordingly
6. Handles graceful shutdown via signal handlers (SIGHUP, SIGINT, SIGQUIT, SIGTERM)

### Status Sources

**Collaboration sources** (`sources/collaboration/`):
- `webex.py` - Webex Teams presence API
- `slack.py` - Slack presence with custom status emoji/text parsing

**Calendar sources** (`sources/calendar/`):
- `office365.py` - Microsoft Graph API free/busy
- `google.py` - Google Calendar API free/busy
- `ics.py` - ICS/iCalendar file support (RFC 5545 compliant, uses `icalendar` + `recurring-ical-events` for proper timezone and recurring event handling)

### Status Precedence

Status determination follows a strict hierarchy:
1. **Source priority:** Collaboration always wins over Calendar (except UNKNOWN/OFF)
2. **Within collaboration:** Webex > Slack
3. **Within calendar:** Office 365 > Google > ICS
4. **Status priority:** Busy > Tentative/Scheduled > Available > Off

### Key Utilities

- `utility/enum.py` - Status enumerations (CollaborationStatus, CalendarStatus, Color)
- `utility/env.py` - Environment variable parsing and validation
- `utility/util.py` - Helper functions including `get_env_or_secret()` for Docker secrets

### Output Targets

- `targets/tuya.py` - Controls Tuya smart bulbs with retry logic and connection management
- `targets/virtual.py` - Virtual light for testing (logs status changes, no hardware required)

## Configuration

All configuration is via environment variables (no config files). Key categories:

- **Sources:** `SOURCES` (comma-separated: webex, slack, office365, google, ics)
- **Target:** `TARGET` (tuya or virtual; default: tuya)
- **Authentication:** Platform-specific tokens/IDs (e.g., `WEBEX_PERSONID`, `SLACK_BOT_TOKEN`, `O365_APPID`, `ICS_URL`)
- **Colors:** `AVAILABLE_COLOR`, `SCHEDULED_COLOR`, `BUSY_COLOR` (predefined names or 24-bit hex)
- **Device:** `TUYA_DEVICE` (JSON with protocol, deviceid, ip, localkey; required only when TARGET=tuya)
- **Behavior:** `SLEEP_SECONDS`, `CALENDAR_LOOKAHEAD`, `LOGLEVEL`, `ACTIVE_DAYS`, `ACTIVE_HOURS_*`

Secrets support `*_FILE` variants for Docker secrets integration.

## CI/CD

GitHub Actions (`.github/workflows/docker-image.yml`) builds multi-platform Docker images:
- Platforms: linux/amd64, linux/arm/v6, linux/arm/v7, linux/arm64
- Triggers: PRs to main (build only), pushes with `v*` tags (build + push to Docker Hub)
- Published to: `portableprogrammer/status-light`

## Documentation

When making changes, update documentation **before** suggesting commits:
- `README.md` - User-facing documentation for environment variables, setup, and usage
- `CLAUDE.md` - Developer guidance for Claude Code (this file)

Keep both files in sync with code changes, especially for:
- New or modified environment variables
- New dependencies in `requirements.txt`
- Architecture changes (new sources, targets, utilities)
- Configuration options
