# Status-Light
A basic status light that will show when I'm available or not. This was inspired by [matthewf01's](https://github.com/matthewf01) [WebexTeams-Status-Box](https://github.com/matthewf01/Webex-Teams-Status-Box)

Status-Light will connect to multiple status sources (currently Cisco Webex and Microsoft Office 365), retrieve the current status of each, and then determine the most-busy status. It will then display this status on a remote RGB LED bulb (currently Tuya).

By default, Webex `call`, `meeting`, `donotdisturb`, or `presenting` statuses will show a red light, Office 365 `busy` and `tentative` statuses will show an orange light, and Webex `active` status will show a green light. All other statuses will turn the light off (i.e. `inactive` in Webex and `free` in Office 365).

## Docker Usage Example
### Commandline with Webex only
``` shell
docker run -d \ 
  --name status-light \
  -e "SOURCES=Webex" \ 
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

## Environment Variables
### `SOURCES`
*Optional*

Available values: `Webex`, `Office365`

Default value: `SOURCES=Webex,Office365`

If specificed, requires at least one of the available options. This will control which services Status-Light uses to determine overall availability status.

### Colors: `AVAILABLE_COLOR`, `SCHEDULED_COLOR`, and `BUSY_COLOR`
*Optional*

Available values: 
* `red` (`ff0000`)
* `yellow` (`ffff00`)
* `orange` (`ff9000`)
* `green` (`00ff00`)
* `blue` (`0000ff`)
* or any 24-bit RGB values (i.e. `000000` - `ffffff`)

Default values:
* `AVAILABLE_COLOR=green`
* `SCHEDULED_COLOR=orange`
* `BUSY_COLOR=red`

**Note:** Status-Light makes no attempt to handle invalid values in these variables. Any error parsing the color will cause Status-Light to revert to the default color for that variable.

### Statuses: `AVAILABLE_STATUS`, `SCHEDULED_STATUS`, `BUSY_STATUS`, and `OFF_STATUS`
*Optional*

Available values: 
* Webex
  * `active`
  * `call`
  * `donotdisturb`
  * `inactive`
  * `meeting`
  * `pending` - The "in-between" status used while attempting to join a meeting
  * `presenting`

* Office 365
  * `free`
  * `tentative`
  * `busy`
  * `outofoffice`
  * `workingelsewhere`

Default values:
* `AVAILABLE_STATUS=active`
* `SCHEDULED_STATUS=busy,tentative`
* `BUSY_STATUS=call,donotdisturb,meeting,presenting,pending`
* `OFF_STATUS=inactive,outofoffice,free,unknown`

**Note 1:** Status-Light makes no attempt to handle invalid values in a list. In the case of an error, Status-Light will simply revert to the default value for that list.

**Note 2:** Status-Light makes no attempt to ensure that any given status is present in only a single list. In the case of a status in multple lists, the order of precedence below applies as well. This can have the unintended side effect of the light cycling through different colors (or even states, if it's turned off first) before landing on the chosen color/state.

#### Status Precedence
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

### `TUYA_DEVICE`
*Required*

Status-Light requires a [Tuya](https://www.tuya.com/) device, which are white-boxed and sold under many brand names. For example, the Tuya light working in the current environment is an [Above Lights](http://alabovelights.com/) [Smart Bulb 9W, model AL1](http://alabovelights.com/pd.jsp?id=17).

Status-Light uses the [tuyaface](https://github.com/TradeFace/tuyaface/) module for Tuya communication.

To retreive your TUYA_DEVICE credentials, follow [codetheweb's](https://github.com/codetheweb) [setup document](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) for [tuyapi](https://github.com/codetheweb/tuyapi).

    ex: "TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }"

**Note 1:** Status-Light will accept an FQDN instead of IP, as long as the name can be resolved. Tuya devices will typically register themselves with the last 6 digits of the device ID, for example `ESP_xxxxxx.local`.

**Note 2:** For Status-Light's purposes, protocol can be 3.0+, but some older devices may not function correctly with the newer protocols, so this may have to be adjusted.

### Webex: `WEBEX_PERSONID` and `WEBEX_BOTID`
*Required if `Webex` is present in `SOURCES`*

Status-Light uses the [webexteamssdk](https://github.com/CiscoDevNet/webexteamssdk/) module for Webex status lookup.

To retrieve your `WEBEX_PERSONID` and `WEBEX_BOTID` creds, see below:
* Temporary `WEBEX_BOTID` token that expires in 12 hours, useful for testing
  * https://developer.webex.com/docs/api/getting-started
* Permanent `WEBEX_BOTID` token that never expires. You'll need to create a bot at the site below
  * https://developer.webex.com/my-apps/new/bot
* Your `WEBEX_PERSONID` from Webex:
  * https://developer.webex.com/docs/api/v1/people/get-my-own-details
  * Sign into your Webex account, then under the "Try It" section, click "Run"
  * Copy the value id from the response shown

### Office 365: `O365_APPID`, `O365_APPSECRET`, and `O365_TOKENSTORE`
*Required if `Office365` is present in `SOURCES`*

Status-Light uses the [python-o365](https://github.com/O365/python-o365/) module for Office 365 status lookup.

To retrieve your `O365_APPID` and `O365_APPSECRET` creds, follow [Python O365's](https://github.com/O365) [usage and authentication guide](https://github.com/O365/python-o365#usage).
An optional variable, `O365_TOKENSTORE`, defines a writable location on disk where the Office 365 tokens are stored. This location should be protected from other users. The default is `~`.
