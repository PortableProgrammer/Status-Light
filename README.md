# Status-Light

A basic status light that will show when I'm available or not. This was inspired by [matthewf01's](https://github.com/matthewf01) [WebexTeams-Status-Box](https://github.com/matthewf01/Webex-Teams-Status-Box), for basically the same reason: My 5-year-old needs some way to tell if he can run in screaming at me while I'm working from home.

Status-Light will connect to multiple status sources (currently Cisco Webex and Microsoft Office 365), retrieve the current status of each, and then determine the most-busy status. It will then display this status on a remote RGB LED bulb (currently Tuya).

By default, Webex `call`, `meeting`, `donotdisturb`, or `presenting` statuses will show a red light, Office 365 `busy` and `tentative` statuses will show an orange light, and Webex `active` status will show a green light. All other statuses will turn the light off (i.e. `inactive` in Webex and `free` in Office 365).

## Contents

- [Python Usage Example](#python-usage-example)
- [Docker Usage Example](#docker-usage-example)
  - [Commandline with Webex only](#commandline-with-webex-only)
  - [Compose with all options](#compose-with-all-options)
  - [Compose with secrets](#compose-with-secrets)
- [Environment Variables](#environment-variables)
  - [`SOURCES`](#-sources-)
  - [Statuses](#--statuses--)
    - [`AVAILABLE_STATUS`](#-available-status-)
    - [`SCHEDULED_STATUS`](#-scheduled-status-)
    - [`BUSY_STATUS`](#-busy-status-)
    - [`OFF_STATUS`](#-off-status-)
    - [Status Precedence](#--status-precedence--)
  - [Colors](#--colors--)
    - [`AVAILABLE_COLOR`](#-available-color-)
    - [`SCHEDULED_COLOR`](#-scheduled-color-)
    - [`BUSY_COLOR`](#-busy-color-)
  - [Tuya](#--tuya--)
    - [`TUYA_DEVICE`](#-tuya-device-)
    - [`TUYA_BRIGHTNESS`](#-tuya-brightness-)
  - [Webex](#--webex--)
    - [`WEBEX_PERSONID`](#-webex-personid-)
    - [`WEBEX_BOTID`](#-webex-botid-)
  - [Office 365](#--office-365--)
    - [`O365_APPID`](#-o365-appid-)
    - [`O365_APPSECRET`](#-o365-appsecret-)
    - [`O365_TOKENSTORE`](#-o365-tokenstore-)
  - [`SLEEP_SECONDS`](#-sleep-seconds-)
  - [`LOGLEVEL`](#-loglevel-)

## Python Usage Example

``` shell
SOURCES=webex \
TUYA_DEVICE="{ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }" \
WEBEX_PERSONID=xxx \
WEBEX_BOTID=xxx \
python -u /path/to/src/status-light.py
```

## Docker Usage Example

### Commandline with Webex only

``` shell
docker run -d \
  --name status-light \
  -e "SOURCES=webex" \
  -e "TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }" \
  -e "WEBEX_PERSONID=xxx" \
  -e "WEBEX_BOTID=xxx" \
  portableprogrammer/status-light:latest
```

### Compose with all options

``` dockerfile
version: '3.7'
services:

  status-light:
    image: portableprogrammer/status-light:latest
    environment:
      - "SOURCES=Webex,Office365"
      - "AVAILABLE_COLOR=green"
      - "SCHEDULED_COLOR=orange"
      - "BUSY_COLOR=red"
      - "AVAILABLE_STATUS=active"
      - "SCHEDULED_STATUS=busy,tentative"
      - "BUSY_STATUS=call,donotdisturb,meeting,presenting,pending"
      - "OFF_STATUS=inactive,outofoffice,free,unknown"
      - "TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }"
      - "TUYA_BRIGHTNESS=128"
      - "WEBEX_PERSONID=xxx"
      - "WEBEX_BOTID=xxx"
      - "O365_APPID=xxx"
      - "O365_APPSECRET=xxx"
      - "O365_TOKENSTORE=/data"
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
  - `Webex`
  - `Office365`
- Default value: `Webex,Office365`

If specificed, requires at least one of the available options. This will control which services Status-Light uses to determine overall availability status.

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
  - Office 365
    - `free`
    - `tentative`
    - `busy`
    - `outofoffice`
    - `workingelsewhere`

#### `AVAILABLE_STATUS`

- Default value: `active`
- By default, denotes that there is no active call or meeting right now, and no meetings scheduled within the next `5` minutes.

#### `SCHEDULED_STATUS`

- Default value: `busy,tentative`
- By default, denotes that there is no active call or meeting right now, but a meeting is scheduled within the next `5` minutes.

#### `BUSY_STATUS`

- Default value: `call,donotdisturb,meeting,presenting,pending`
- By default, denotes that there is an active call or meeting right now, or (in the case of `donotdisturb` or `presenting`) some other reason why the user could be considered *busy*.

#### `OFF_STATUS`

- Default value: `inactive,outofoffice,free,unknown`
- By default, denotes that the user is not working now.
- In the case of `unknown`, this is essentially a fail-safe. If we can't determine the status, just turn the light off.
- In the case of `outofoffice`, this is a personal preference. *I* don't need Status-Light to tell my family that I'm out of the office; they can see that.
- In the case of `free`, there are a few reasons why it's in `OFF_STATUS` by default.
  - Typically, if the user is asking for both Webex and Office 365, the user will be `active` and `free` simultaneously, so `active` will always win.
  - Since there is no Office 365 status for "out of work hours", Status-Light makes a  determination of `free`/`busy`/`tentative` by checking the user's availability within the next `5` minutes. In this scenario, at the end of the working day, the user is technically `free`, but there's no reason to keep the light on all night.
  - In the case that Webex is not selected as a source, it is recommended to move `free` to `AVAILABLE_STATUS`, but the caveat above will apply in that scenario: the light may stay on all the time.
  

**Note 1:** Status-Light makes no attempt to handle invalid values in a list. In the case of an error, Status-Light will simply revert to the default value for that list.

**Note 2:** Status-Light makes no attempt to ensure that any given status is present in only a single list. In the case of a status in multiple lists, the order of precedence below applies as well. This can have the unintended side effect of the light cycling through different colors (or even states, if it's turned off first) before landing on the chosen color/state.

#### **Status Precedence**

Since the "most-busy" status should win when selecting a color, typically the Webex status will take precedence over Office 365. For example, if your Office 365 status is `busy` (you're scheduled to be in a meeting), and your Webex status is `meeting` (you're actively in the meeting), the Webex `meeting` status would take precedence, given the default values listed above. Generally, precedence is `BUSY_STATUS`, then `SCHEDULED_STATUS`, followed by `AVAILABLE_STATUS`, and finally `OFF_STATUS`. In more specific terms, the way Status-Light handles precedence is:

``` python
# Webex status always wins except in specific scenarios
currentStatus = webexStatus
if (webexStatus in availableStatus or webexStatus in offStatus) and officeStatus not in offStatus:
  # Use the Office 365 status instead
  currentStatus = officeStatus

if currentStatus in offStatus:
  # Turn off the light

if currentStatus in availableStatus:
  # Set availableColor

if currentStatus in scheduledStatus:
  # Set scheduledColor

if currentStatus in busyStatus:
  # Set busyColor
```

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

### **Tuya**

#### `TUYA_DEVICE`

- *Required*

Status-Light requires a [Tuya](https://www.tuya.com/) device, which are white-boxed and sold under many brand names. For example, the Tuya light working in the current environment is an [Above Lights](http://alabovelights.com/) [Smart Bulb 9W, model AL1](http://alabovelights.com/pd.jsp?id=17).

Status-Light uses the [tuyaface](https://github.com/TradeFace/tuyaface/) module for Tuya communication.

To retreive your TUYA_DEVICE credentials, follow [codetheweb's](https://github.com/codetheweb) [setup document](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) for [tuyapi](https://github.com/codetheweb/tuyapi).

``` shell
Example:
"TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }"
```

**Docker Secrets:** This variable can instead be specified in a secrets file, using the `TUYA_DEVICE_FILE` variable.

**Note 1:** Status-Light will accept an FQDN instead of IP, as long as the name can be resolved. Tuya devices will typically register themselves with the last 6 digits of the device ID, for example `ESP_xxxxxx.local`.

**Note 2:** For Status-Light's purposes, protocol can be 3.0+, but some older devices may not function correctly with the newer protocols, so this may have to be adjusted.

#### `TUYA_BRIGHTNESS`

- *Optional*
- Acceptable Range: `32`-`255`
- Default Value: `128`

Set the brightness of your Tuya light. This is an 8-bit `integer` corresponding to a percentage from 0%-100% (though Tuya lights typically don't accept a brightness value below `32`). Status-Light defaults to 50% brightness, `128`.

### **Webex**

#### `WEBEX_PERSONID`

#### `WEBEX_BOTID`

- *Required if `Webex` is present in `SOURCES`*

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

### **Office 365**

#### `O365_APPID`

#### `O365_APPSECRET`

- *Required if `Office365` is present in `SOURCES`*

Status-Light uses the [python-o365](https://github.com/O365/python-o365/) module for Office 365 status lookup.

To retrieve your `O365_APPID` and `O365_APPSECRET` creds, follow [Python O365's](https://github.com/O365) [usage and authentication guide](https://github.com/O365/python-o365#usage).

**Docker Secrets:** These variables can instead be specified in secrets files, using the `O365_APPID_FILE` and `O365_APPSECRET_FILE` variables.

#### `O365_TOKENSTORE`

- *Optional*
- Acceptable value: Any writable location on disk, e.g. `/path/to/token/`
- Default value: `~`

Defines a writable location on disk where the Office 365 tokens are stored. This location should be protected from other users.

**Note:** This path is directory only. The python-o365 module will expect to persist a file within the directory supplied.

### `SLEEP_SECONDS`

- *Optional*
- Acceptable range: `5`-`60`
- Default value: `5`

Set the number of seconds between status checks.

### `LOGLEVEL`

- *Optional*
- Acceptable values, documented [here](https://docs.python.org/3/library/logging.html#levels):
  - `CRITICAL`
  - `ERROR`
  - `WARNING`
  - `INFO`
  - `DEBUG`
- Default value: `WARNING`

Sets the log level for Status-Light.
