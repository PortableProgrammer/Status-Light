# Status-Light

A basic status light that will show when I'm available or not. This was inspired by [matthewf01's](https://github.com/matthewf01) [WebexTeams-Status-Box](https://github.com/matthewf01/Webex-Teams-Status-Box), for basically the same reason: My 5-year-old needs some way to tell if he can run in screaming at me while I'm working from home.

Status-Light will connect to multiple status sources (e.g. collaboration suites like Webex and calendaring applications like Office 365 and Google), retrieve the current status of each, and then determine the most-busy status. It will then display this status on a remote RGB LED bulb.

By default, `call`, `meeting`, `donotdisturb`, or `presenting` collaboration statuses will show a red light, `busy` and `tentative` calendar statuses will show an orange light, and the `active` collaboration status will show a green light. All other statuses will turn the light off (i.e. `inactive` in Webex and `free` in Office 365).

## Python Usage Example

``` shell
SOURCES=webex \
TUYA_DEVICE='{ "protocol": "3.3", "deviceid": "xxx", "ip": "yyy", "localkey": "zzz" }' \
WEBEX_PERSONID=xxx \
WEBEX_BOTID=xxx \
python -u /path/to/src/status-light.py
```

## Docker Usage Examples

### Commandline with Webex only

``` shell
docker run -d \
  --name status-light \
  -e "SOURCES=webex" \
  -e 'TUYA_DEVICE={ "protocol": "3.3", "deviceid": "xxx", "ip": "yyy", "localkey": "zzz" }' \
  -e "WEBEX_PERSONID=xxx" \
  -e "WEBEX_BOTID=xxx" \
  portableprogrammer/status-light:latest
```

### Compose with all default options

``` dockerfile
version: '3.7'
services:

  status-light:
    image: portableprogrammer/status-light:latest
    environment:
      - "SOURCES=Webex,Office365"
      - "TARGET=tuya"
      - "AVAILABLE_COLOR=green"
      - "SCHEDULED_COLOR=orange"
      - "BUSY_COLOR=red"
      - "AVAILABLE_STATUS=active"
      - "SCHEDULED_STATUS=busy,tentative"
      - "BUSY_STATUS=call,donotdisturb,meeting,presenting,pending"
      - "OFF_STATUS=inactive,outofoffice,free,unknown"
      - 'TUYA_DEVICE={ "protocol": "3.3", "deviceid": "xxx", "ip": "yyy", "localkey": "zzz" }'
      - "TUYA_BRIGHTNESS=128"
      - "WEBEX_PERSONID=xxx"
      - "WEBEX_BOTID=xxx"
      - "O365_APPID=xxx"
      - "O365_APPSECRET=xxx"
      - "O365_TOKENSTORE=/data"
      - "GOOGLE_TOKENSTORE=/data"
      - "GOOGLE_CREDENTIALSTORE=/data"
      - "ICS_URL=https://example.com/calendar.ics"
      - "ICS_CACHESTORE=/data"
      - "ICS_CACHELIFETIME=30"
      - "SLACK_USER_ID=xxx"
      - "SLACK_BOT_TOKEN=xxx"
      - "SLACK_CUSTOM_AVAILABLE_STATUS=''"
      - "SLACK_CUSTOM_SCHEDULED_STATUS=':spiral_calendar_pad: In a meeting'"
      - "SLACK_CUSTOM_BUSY_STATUS=':headphones: In a huddle',':slack_call:',':no_entry_sign:',':no_entry: Do not disturb'"
      - "SLACK_CUSTOM_OFF_STATUS=':no_entry: Out of office',':airplane:',':palm_tree: Vacationing'"
      - "ACTIVE_DAYS=Monday,Tuesday,Wednesday,Thursday,Friday"
      - "ACTIVE_HOURS_START=08:00:00"
      - "ACTIVE_HOURS_END=17:00:00"
      - "CALENDAR_LOOKAHEAD=5"
      - "SLEEP_SECONDS=5"
      - "LOGLEVEL=INFO"
    volumes:
      - type: bind
        source: /path/to/tokenstore
        target: /data
```

### Compose with secrets

**Note:** This method requires that you have previously defined the secrets using the [`docker secret create` command](https://docs.docker.com/engine/reference/commandline/secret_create/).

``` dockerfile
version: '3.7'
services:

  status-light:
    image: portableprogrammer/status-light:latest
    environment:
      - "TUYA_DEVICE_FILE=/run/secrets/tuya-device-secret-v1"
      - "WEBEX_PERSONID_FILE=/run/secrets/webex-personid-secret-v1"
      - "WEBEX_BOTID_FILE=/run/secrets/webex-botid-secret-v1"
      - "O365_APPID_FILE=/run/secrets/o365-appid-secret-v1"
      - "O365_APPSECRET_FILE=/run/secrets/o365-appsecret-secret-v3"
      - "O365_TOKENSTORE=/data"
    volumes:
      - type: bind
        source: /path/to/tokenstore
        target: /data
    secrets:
      - tuya-device-secret-v1
      - webex-personid-secret-v1
      - webex-botid-secret-v1
      - o365-appid-secret-v1
      - o365-appsecret-secret-v3

secrets:
  tuya-device-secret-v1:
    external: true
  webex-personid-secret-v1:
    external: true
  webex-botid-secret-v1:
    external: true
  o365-appid-secret-v1:
    external: true
  o365-appsecret-secret-v3:
    external: true
```

## Environment Variables

### `SOURCES`

- *Optional*
- Available values:
  - `webex`
  - `slack`
  - `office365`
  - `google`
  - `ics`
- Default value: `webex,office365`

If specificed, requires at least one of the available options. This will control which services Status-Light uses to determine overall availability status.

---

### `TARGET`

- *Optional*
- Available values:
  - `tuya` - Physical Tuya smart bulb (requires `TUYA_DEVICE`)
  - `virtual` - Virtual light that logs status changes (for testing)
- Default value: `tuya`

Specifies the output target for status display. Use `virtual` for testing without hardware.

---

### **Statuses**

- *Optional*
- Available values:
  - Webex
    - `active`
    - `call`
    - `donotdisturb`
    - `inactive`
    - `meeting`
    - `pending`
    - `presenting`
  - Slack
    - `active`
    - `inactive`
  - Office 365
    - `free`
    - `tentative`
    - `busy`
    - `outofoffice`
    - `workingelsewhere`
  - Google
    - `free`
    - `busy`
  - ICS
    - `free`
    - `tentative`
    - `busy`

#### `AVAILABLE_STATUS`

- Default value: `active`
- By default, denotes that there is no ongoing collaboration call or meeting, and no calendar meetings scheduled within the configured [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) interval.
  - This is the default *not busy* state. See [`OFF_STATUS`](#off_status) for an explanation of why the calendar `free` status is not included in this list by default, and why you may want to change that.

#### `SCHEDULED_STATUS`

- Default value: `busy,tentative`
- By default, denotes that there is no ongoing collaboration call or meeting, but a calendar meeting, that was either accepted or tentatively accepted, is scheduled within the configured [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) interval.
  - This is the default *about to be busy* state.

#### `BUSY_STATUS`

- Default value: `call,donotdisturb,meeting,presenting,pending`
- By default, denotes that there is an ongoing collaboration call or meeting, or (in the case of `donotdisturb` or `presenting`) some other reason why the user could be considered busy.
  - This is the default *busy* state.
- If the Webex "Show when in a calendar meeting" option is selected, and `webex` is present in [`SOURCES`](#sources), Webex will return a `meeting` status for any connected calendars.

#### `OFF_STATUS`

- Default value: `inactive,outofoffice,workingelsewhere,free,unknown`
- By default, denotes that the user is not working now.
  - This is the default *after hours* state.
- In the case of `unknown`, this is essentially a fail-safe. If we can't determine the status, just turn the light off.
- In the case of `outofoffice` and `workingelsewhere`, this is a personal preference. I don't need Status-Light to tell my family that I'm somewhere else; they can see that.
- In the case of `free`, there are a few reasons why it's in `OFF_STATUS` by default.
  - Typically, if the user is asking for both collaboration and calendar statuses, the user will be `active` (from collaboration) and `free` (from calendar) simultaneously, so `active` will always win.
  - Status-Light makes a determination of `free`/`busy`/`tentative` by checking the user's calendar availability within the configured [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) interval. There is typically no 'off-hours' status in calendaring applications, which means, at the end of the working day, the user is technically `free`. In that instance, the light would be on during off hours, showing the selected [`AVAIALBLE_COLOR`](#available_color). Again, this is a personal preference; I don't want the light on while I'm not at work, and I am using Webex to handle [`AVAILABLE_STATUS`](#available_status).
  - This behavior can be further refined with the [`ACTIVE_*`](#active-times) variables.
  - In the case that no collaboration sources are present in [`SOURCES`](#sources), it is recommended to move `free` to [`AVAILABLE_STATUS`](#available_status), but the caveat above will apply in that scenario: the light may stay on all the time.

**Note 1:** Status-Light makes no attempt to handle invalid values in a list. In the case of an error, Status-Light will simply revert to the default value for that list.

**Note 2:** Status-Light makes no attempt to ensure that any given status is present in only a single list. In the case of a status in multiple lists, the order of precedence below applies as well.

#### **Status Precedence**

Since the "most-busy" status should win when selecting a color, typically the collaboration status will take precedence over calendars. For example, if your calendar status is `busy` (you're scheduled to be in a meeting), and your collaboration status is `meeting` (you're actively in the meeting), the collaboration status would take precedence, given the default values listed above. Generally, precedence is [`BUSY_STATUS`](#busy_status), then [`SCHEDULED_STATUS`](#scheduled_status), followed by [`AVAILABLE_STATUS`](#available_status), and finally [`OFF_STATUS`](#off_status). In more specific terms, the way Status-Light handles precedence is:

``` python
# Collaboration status always wins except in specific scenarios
# Webex currently takes precendence over Slack
currentStatus = webexStatus
if webexStatus == const.Status.unknown or webexStatus in offStatus:
  # Fall through to Slack
  currentStatus = slackStatus

if (currentStatus in availableStatus or currentStatus in offStatus)
  and (officeStatus not in offStatus or googleStatus not in offStatus
       or icsStatus not in offStatus):

  # Office 365 currently takes precedence over Google, Google over ICS
  if (officeStatus != const.Status.unknown):
    currentStatus = officeStatus
  elif (googleStatus != const.Status.unknown):
    currentStatus = googleStatus
  else:
    currentStatus = icsStatus

if currentStatus in availableStatus:
  # Get availableColor

if currentStatus in scheduledStatus:
  # Get scheduledColor

if currentStatus in busyStatus:
  # Get busyColor

if currentColor != None:
  # Set currentColor
elif currentStatus in offStatus:
  # Turn off the light
```

---

### **Slack Custom Statuses**

While Slack only offers the `active` and `inactive` presence flags, it also offers the ability to set custom emoji and text statuses. By default, Slack uses several of these to indicate a more granular status, for example, `:slack_call:` or `:spiral_calendar_pad: In a meeting`. Status-Light can read this custom emoji and text to infer a more specific status than `active` or `inactive`. For example, you may be `active` in Slack, but also in a Slack Call (`:slack_call:`) or a Slack Huddle (`:headphones: In a huddle`). In this instance, Status-Light can interpret the custom status message as `CALL`, and set the appropriate color.

These options accept a list of strings that should match the beginning of the Slack custom status.
Take the following scenario:

```python
SLACK_BUSY_STATUS = [':no_entry_sign: Do Not Disturb']
BUSY_STATUS = [CALL, DONOTDISTURB, MEETING, PRESENTING, PENDING]
AVAILABLE_STATUS = ACTIVE
slack.Presence = ACTIVE
slack.CustomStatus = ':no_entry_sign: Do not disturb, I need to finish project X today!'
```

In the example above, the Slack custom status would match (since it is a case-insensitive comparison), and therefore take precedence over the Slack presence, causing Status-Light to treat Slack as `BUSY` instead of `AVAILABLE`.

#### `SLACK_CUSTOM_AVAILABLE_STATUS`

- *Optional*, case-insensitive
- Default value: `''`
- Slack's `active` presence lines up nicely with the default [`AVAILABLE_STATUS`](README.md#availablestatus), so there is no default custom override for this option.

#### `SLACK_CUSTOM_SCHEDULED_STATUS`

- *Optional*, case-insensitive
- Default value: `':spiral_calendar_pad: In a meeting'`
- If you have a calendaring source configured in Slack but not in Status-Light, this default [`SCHEDULED_STATUS`](README.md#scheduledstatus) is an easy way to obtain both collaboration and calendar status from a single source. If you also have the same calendaring source configured in Status-Light, this will duplicate it, assuming that they're fully in sync.

#### `SLACK_CUSTOM_BUSY_STATUS`

- *Optional*, case-insensitive
- Default value: `':no_entry_sign:',':no_entry: Do not disturb'`
- This custom status also includes Slack A/V collaboration modes by default, like [Huddles](https://slack.com/help/articles/4402059015315-Use-huddles-in-Slack) and [Calls](https://slack.com/help/articles/216771908-Make-calls-in-Slack).

**Note 1:** For the default Call and Huddle custom statuses to work, you must have selected `Set my status to...` for Calls and Huddles in the Slack preferences.

**Note 2:** Slack, by default, will not automatically change your custom status when you join a Call or Huddle, if you already have one set. In this instance, Status-Light will react to your existing custom status and other Source statuses.

#### `SLACK_CUSTOM_OFF_STATUS`

- *Optional*, case-insensitive
- Default value: `':no_entry: Out of office',':airplane:',':palm_tree: vacationing'`
- If you have a calendaring source configured in Slack but not in Status-Light, this default [`OFF_STATUS`](README.md#offstatus) is an easy way to obtain both collaboration and calendar status from a single source. If you also have the same calendaring source configured in Status-Light, this will duplicate it, assuming that they're fully in sync.

---

### **Colors**

- *Optional*
- Available values:
  - `red` (`ff0000`)
  - `yellow` (`ffff00`)
  - `orange` (`ff9000`)
  - `green` (`00ff00`)
  - `blue` (`0000ff`)
  - or any 24-bit RGB values (i.e. `000000` - `ffffff`)

#### `AVAILABLE_COLOR`

- Default value: `green`

#### `SCHEDULED_COLOR`

- Default value: `orange`

#### `BUSY_COLOR`

- Default value: `red`

---

### **Tuya**

**Note:** Tuya configuration is only required when [`TARGET`](#target) is set to `tuya` (the default). If using `TARGET=virtual`, you can skip this section.

#### `TUYA_DEVICE`

- *Required if [`TARGET`](#target) is `tuya`*

Status-Light supports [Tuya](https://www.tuya.com/) devices, which are white-boxed and sold under many brand names. For example, the Tuya light working in the current environment is an [Above Lights](http://alabovelights.com/) [Smart Bulb 9W, model AL1](http://alabovelights.com/pd.jsp?id=17).

Status-Light uses the [tuyaface](https://github.com/TradeFace/tuyaface/) module for Tuya communication.

To retreive your `TUYA_DEVICE` credentials, follow [codetheweb's](https://github.com/codetheweb) [setup document](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) for [tuyapi](https://github.com/codetheweb/tuyapi).

Status-Light expects a valid JSON object in this variable. Specifically, attribute names (e.g. `protocol`) must be in double quotes. This may mean you need to use single quotes to surround the entire variable. See the example below.

Example `TUYA_DEVICE` value:

``` shell
'TUYA_DEVICE={ "protocol": "3.3", "deviceid": "xxx", "ip": "yyy", "localkey": "zzz" }'
```

**Docker Secrets:** This variable can instead be specified in a secrets file, using the `TUYA_DEVICE_FILE` variable.

**Note:** Status-Light will accept an FQDN instead of IP, as long as the name can be resolved. Tuya devices will typically register themselves with the last 6 digits of the device ID, for example `ESP_xxxxxx.local`.

#### `TUYA_BRIGHTNESS`

- *Optional, only valid if [`TARGET`](#target) is `tuya`*
- Acceptable range: `32`-`255`
- Default value: `128`

Set the brightness of your Tuya light. This is an 8-bit `integer` corresponding to a percentage from 0%-100% (though Tuya lights typically don't accept a brightness value below `32`). Status-Light defaults to 50% brightness, `128`.

---

### **Webex**

#### `WEBEX_PERSONID`

#### `WEBEX_BOTID`

- *Required if `webex` is present in [`SOURCES`](#sources)*

Status-Light uses the [webexteamssdk](https://github.com/CiscoDevNet/webexteamssdk/) module for Webex status lookup.

To retrieve your `WEBEX_PERSONID` and `WEBEX_BOTID` creds, see below:

- Temporary `WEBEX_BOTID` token that expires in 12 hours, useful for testing
  - <https://developer.webex.com/docs/api/getting-started>
- Permanent `WEBEX_BOTID` token that never expires. You'll need to create a bot at the site below
  - <https://developer.webex.com/my-apps/new/bot>
- Your `WEBEX_PERSONID` from Webex:
  - <https://developer.webex.com/docs/api/v1/people/get-my-own-details>
  - Sign into your Webex account, then under the "Try It" section, click "Run"
  - Copy the value id from the response shown

**Docker Secrets:** These variables can instead be specified in secrets files, using the `WEBEX_PERSONID_FILE` and `WEBEX_BOTID_FILE` variables.

---

### **Slack**

#### `SLACK_USER_ID`

- *Required if `slack` is present in [`SOURCES`](#sources)*
- The ID of the user presence to monitor.
  - Retrieve by navigating to the user's profile, then selecting `More` and `Copy member ID`

#### `SLACK_BOT_TOKEN`

- *Required if `slack` is present in [`SOURCES`](#sources)*

To retrieve your `SLACK_BOT_TOKEN`, see below:

- Easy: Slack App Tutorial
  - <https://github.com/slackapi/python-slack-sdk/tree/main/tutorial>
  - Follow Step 1 and assign the following Scopes to the Bot Token
    - `users:read`
- Advanced: Create a Slack App by hand
  - <https://developer.webex.com/my-apps/new/bot>
  - Assign the following Scopes to the Bot Token
    - `users:read`

**Docker Secrets:** This variable can instead be specified in a secrets file, using the `SLACK_BOT_TOKEN_FILE` variable.

**Note:** The `SLACK_BOT_TOKEN` is Workspace-specific, meaning you will need to create a new bot for each Slack Workspace.

---

### **Office 365**

**Note:** See [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) to configure lookahead timing for Calendar sources.

#### `O365_APPID`

#### `O365_APPSECRET`

- *Required if `office365` is present in [`SOURCES`](#sources)*

Status-Light uses the [python-o365](https://github.com/O365/python-o365/) module for Office 365 status lookup.

To retrieve your `O365_APPID` and `O365_APPSECRET` creds, follow [Python O365's](https://github.com/O365) [usage and authentication guide](https://github.com/O365/python-o365#usage).

**Docker Secrets:** These variables can instead be specified in secrets files, using the `O365_APPID_FILE` and `O365_APPSECRET_FILE` variables.

#### `O365_TOKENSTORE`

- *Optional, only valid if `office365` is present in [`SOURCES`](#sources)*
- Acceptable value: Any writable location on disk, e.g. `/path/to/token/`
- Default value: `~`

Defines a writable location on disk where the Office 365 tokens are stored. This location should be protected from other users.

**Note:** This path is directory only. The python-o365 module will expect to persist a file within the directory supplied.

---

### **Google**

**Note:** See [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) to configure lookahead timing for Calendar sources.

#### `GOOGLE_CREDENTIALSTORE`

- *Optional, only valid if `google` is present in [`SOURCES`](#sources)*
- Acceptable value: Any writable location on disk, e.g. `/path/to/creds/`
- Default value: *preconfigured key*

Defines a writable location on disk where the Google application credentials are stored. This location should be protected from other users.

Status-Light is preconfigured with a Google API key that allows `freebusy` access to Google calendars for the express purpose of reading free/busy status. If you prefer to roll your own API key, you may mount your own `client_secret.json` in any directory and provide that path in this variable.

**Note:** This path is directory only. Status-Light expects to find a file named `client_secret.json` within the directory supplied.

#### `GOOGLE_TOKENSTORE`

- *Optional, only valid if `google` is present in [`SOURCES`](#sources)*
- Acceptable value: Any writable location on disk, e.g. `/path/to/token/`
- Default value: `~`

Defines a writable location on disk where the Google tokens are stored. This location should be protected from other users.

##### **Authorizing Status-Light**

If you are running Status-Light locally, the first time the authentication flow runs, you will see a Google authentication prompt in your default browser, and responding to it should authorize Status-Light successfully, storing `token.json` in the directory specified here.

Since Google has [deprecated](https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html#instructions-oob) OOB authentication flows for headless devices, if you are running Status-Light headless (e.g. in a Docker container), you will need to obtain your `token.json` file manually and place it into the directory specified here.

**Note:** This path is directory only. Status-Light expects to persist a file within the directory supplied.

---

### **ICS**

**Note:** See [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) to configure lookahead timing for Calendar sources.

Status-Light uses the [icalendar](https://github.com/collective/icalendar) and [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events) libraries to parse ICS files. These libraries correctly handle recurring events and cross-timezone event matching (e.g., a Pacific time event will be correctly detected when running in Mountain time).

Status-Light's ICS source implements RFC 5545 compliant status detection based on the `TRANSP` (transparency) and `STATUS` properties of calendar events:

| Event Properties | Status-Light Status |
|-----------------|---------------------|
| `TRANSP=TRANSPARENT` | `free` (event doesn't block time) |
| `STATUS=CANCELLED` | `free` (event was cancelled) |
| `STATUS=TENTATIVE` | `tentative` (maps to BUSY-TENTATIVE in RFC terms) |
| `STATUS=CONFIRMED` or unset | `busy` (default blocking event) |

When multiple events exist in the lookahead window, the "busiest" status wins: `busy` > `tentative` > `free`.

#### `ICS_URL`

- *Required if `ics` is present in [`SOURCES`](#sources)*

The URL to an ICS (iCalendar) file. This can be any publicly accessible URL that returns a valid `.ics` file, such as:
- A shared Google Calendar ICS link
- An Office 365 published calendar
- Any other iCalendar-compatible calendar export

Status-Light will fetch this file periodically (controlled by `ICS_CACHELIFETIME`) and check for events within the [`CALENDAR_LOOKAHEAD`](#calendar_lookahead) window.

**Docker Secrets:** This variable can instead be specified in a secrets file, using the `ICS_URL_FILE` variable.

#### `ICS_CACHESTORE`

- *Optional, only valid if `ics` is present in [`SOURCES`](#sources)*
- Acceptable value: Any writable location on disk, e.g. `/path/to/cache/`
- Default value: `~`

Defines a writable location on disk where the cached ICS file is stored.

**Note:** This path is directory only. Status-Light will persist a file named `status-light-ics-cache.ics` within the directory supplied.

#### `ICS_CACHELIFETIME`

- *Optional, only valid if `ics` is present in [`SOURCES`](#sources)*
- Acceptable range: `5`-`60`
- Default value: `30`

Set the number of minutes the cached ICS file remains valid before being re-fetched from the URL. A lower value means more frequent updates but more network requests.

---

### **Active Times**

If you prefer to leave Status-Light running all the time (e.g. headless in a Docker container), you may wish to disable status polling during off hours.

**Note:** This implementation is fairly basic, assuming that active hours are identical on all active days, and that the active hours will start and end on the same day. This may preclude, for example, configuring active hours that span days (e.g. overnights) or differing schedules on specific days.

#### `ACTIVE_DAYS`

A list of days that Status-Light will be actively polling status sources.

- *Optional*
- Acceptable values:
  - `Monday`
  - `Tuesday`
  - `Wednesday`
  - `Thursday`
  - `Friday`
  - `Saturday`
  - `Sunday`
- Default value: `Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday`

#### `ACTIVE_HOURS_START`

#### `ACTIVE_HOURS_END`

A time, in 24-hour format, signifying the start and end of the active hours on any active day.

- *Optional*
- Default values:
  - `ACTIVE_HOURS_START`: `00:00:00`
  - `ACTIVE_HOURS_END`: `23:59:59`

---

### `CALENDAR_LOOKAHEAD`

- *Optional*
- Acceptable range: `5`-`60`
- Default value: `5`

Set the number of minutes that Calendar [`SOURCES`](#sources) lookahead to determine free/busy.

---

### `SLEEP_SECONDS`

- *Optional*
- Acceptable range: `5`-`60`
- Default value: `5`

Set the number of seconds between status checks.

---

### `LOGLEVEL`

- *Optional*
- Acceptable values, documented on [docs.python.org](https://docs.python.org/3/library/logging.html#levels):
  - `CRITICAL`
  - `ERROR`
  - `WARNING`
  - `INFO`
  - `DEBUG`
- Default value: `INFO`

Sets the log level for Status-Light.

**Note:** Setting `LOGLEVEL` to anything above `INFO` may cause you to lose status information. It is recommended you keep this at `INFO` until you are comfortable with the configuration.
