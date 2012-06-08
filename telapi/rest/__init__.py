from telapi.schema import SCHEMA
import os
import exceptions

class ClientMetaClass(type):
    def __new__(meta, classname, bases, classDict):
        # Get all available methods from schema
        return type.__new__(meta, classname, bases, classDict)

class Client(object):
    """TelAPI REST Client

    Instead of passing account_sid and auth_token to this class, you can set
    environment variables `TELAPI_ACCOUNT_SID` and `TELAPI_AUTH_TOKEN`.
    """

    __metaclass__ = ClientMetaClass
    
    def __init__(self, account_sid=None, auth_token=None, *args, **kwargs):
        object.__init__(self)
        self.account_sid = account_sid or os.environ.get('TELAPI_ACCOUNT_SID')
        self.auth_token  = auth_token or os.environ.get('TELAPI_AUTH_TOKEN')

        if not self.account_sid:
            raise exceptions.AccountSidError()

        if not self.auth_token:
            raise exceptions.AccountSidError()

    def call(self):
        pass
