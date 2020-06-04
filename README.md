# Status-Light
A basic status light that will show when I'm available or not. This was inspired by [matthewf01's](https://github.com/matthewf01) [WebexTeams-Status-Box](https://github.com/matthewf01/Webex-Teams-Status-Box)

Status-Light will connect to multiple status sources (currently Cisco Webex and Microsoft Office 365), retrieve the current status of each, and then determine the most-busy status. It will then display this status on a remote RGB LED bulb (currently Tuya).

By default, Webex in-call, meeting, DnD, or presenting statuses will show a red light, Office 365 busy and tentative statuses will show an orange light, and Webex free status will show a green light. All other statuses will turn the light off (i.e. inactive in Webex).

## Tuya setup
To retreive your TUYA_DEVICE credentials, follow [codetheweb's](https://github.com/codetheweb) [setup document](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) for [tuyapi](https://github.com/codetheweb/tuyapi)

## Office 365 setup
To retrieve your O365_APPID and O365_APPSECRET creds, follow [Python O365's](https://github.com/O365) [usage and authentication guide](https://github.com/O365/python-o365#usage).
An optional variable, O365_TOKENSTORE, defines a writable location on disk where the Office 365 tokens are stored. This location should be protected from other users. The default is '~'.

## Webex setup
To retrieve your WEBEX_PERSONID and WEBEX_BOTID creds, follow see below:
* Temporary WEBEX_BOTID token that expires in 12 hours, useful for testing
  * https://developer.webex.com/docs/api/getting-started
* Permanent WEBEX_BOTID token that never expires. You'll need to create a bot at the site below
  * https://developer.webex.com/my-apps/new/bot
* Your WEBEX_PERSONID from Webex:
  * https://developer.webex.com/docs/api/v1/people/get-my-own-details
  * Sign into your Webex account, then under the "Try It" section, click "Run"
  * Copy the value id from the response shown

## Docker Usage
### Commandline
``` docker
docker run -d \ 
  --name status-light \ 
  --restart always \ 
  -e "WEBEX_PERSONID=xxx" \ 
  -e "WEBEX_BOTID=xxx" \ 
  -e "TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }" \ 
  -e "O365_APPID=xxx" \ 
  -e "O365_APPSECRET=xxx" \ 
  -e "O365_TOKENSTORE=/data" \ 
  --mount 'type=bind,src=/path/to/tokenstore,target=/data' \ 
  portableprogrammer/status-light:latest
```
### Compose
``` docker
version: '3.7'
services:

  light:
    image: portableprogrammer/status-light:latest
    container_name: status-light
    environment:
      - "WEBEX_PERSONID=xxx"
      - "WEBEX_BOTID=xxx"
      - "TUYA_DEVICE={ 'protocol': '3.3', 'deviceid': 'xxx', 'ip': 'xxx', 'localkey': 'xxx' }"
      - "O365_APPID=xxx"
      - "O365_APPSECRET=xxx"
      - "O365_TOKENSTORE=/data"
    volumes:
      - type: bind
        source: /path/to/tokenstore
        target: /data
    restart: always
```