# Status-Light
A basic status light that will show when I'm available or not. This was inspired by [matthewf01's](https://github.com/matthewf01) [WebexTeams-Status-Box](https://github.com/matthewf01/Webex-Teams-Status-Box)

## Tuya setup
To retreive your TUYA_DEVICE credentials, follow [codetheweb's](https://github.com/codetheweb) [setup document](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) for [tuyapi](https://github.com/codetheweb/tuyapi)

## Office365 setup
To retrieve your O365_APPID and O365_APPSECRET creds, follow [Python O365's](https://github.com/O365) [usage and authentication guide](https://github.com/O365/python-o365#usage).
An optional variable, O365_TOKENSTORE, defines a writable location on disk where the Office365 tokens are stored. This location should be protected from other users. The default is '~'.

## Webex setup
This retrieve your WEBEX_PERSONID and WEBEX_BOTID creds, follow see below:
* Temporary WEBEX_BOTID token that expires in 12 hours, useful for testing
  * https://developer.webex.com/docs/api/getting-started
* Permanent WEBEX_BOTID token that never expires. You'll need to create a bot at the site below
  * https://developer.webex.com/my-apps/new/bot
* Your WEBEX_PERSONID from Webex:
  * https://developer.webex.com/docs/api/v1/people/get-my-own-details
  * Sign into your Webex account, then under the "Try It" section, click "Run"
  * Copy the value id from the response shown
