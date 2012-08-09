telapi-python
=============

This library interacts with the [TelAPI](http://telapi.com) service. It allows you to use the REST API in a pythonic way to initiate and 
manage outbound calls and SMS messages as well as generate InboundXML to handle incoming calls and SMS messages.


Installation
------------

Download the latest source from https://github.com/telapi/telapi-python/zipball/master or checkout the code, 
then `cd` into the resulting directory and run `python setup.py install`.


Protip
------

Export the `TELAPI_ACCOUNT_SID` and `TELAPI_AUTH_TOKEN` variables in your environment,
such as ~/.profile and you won't have to pass your credentials in when intantiating the client.

Account SID and auth token are both found in the [Dashboard](http://www.telapi.com/dashboard)

```bash
export TELAPI_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
export TELAPI_AUTH_TOKEN='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```


Quick Start
-----------

Account SID and auth token are both found in the [Dashboard](http://www.telapi.com/dashboard)

```python
from telapi import rest

account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token  = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client      = rest.Client(account_sid, auth_token)
account     = client.accounts[client.account_sid]
voice_url   = 'http://db.tt/YtLJgpa8'

# Let's create a call that will dial someone and say "Hello"
account.calls.create(from_number="+15555555555", to_number="+15555555556", url=voice_url)
```


