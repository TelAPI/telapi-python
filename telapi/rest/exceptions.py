class RestError(Exception):
    def __init__(self, message, error_code=None, http_code=None):
        Exception.__init__(self, message)
        self.message    = message
        self.error_code = error_code
        self.http_code  = http_code

class AccountSidError(RestError):
    def __init__(self, message=None, error_code=None, http_code=None):
        message = """Please pass account_sid when instantiating the REST API Client or set the environment variable `TELAPI_ACCOUNT_SID`.\
        An account SID is a 34 character string that starts with the letters 'AC'."""
        RestError.__init__(self, message)

class AuthTokenError(RestError):
    def __init__(self, message=None, error_code=None, http_code=None):
        message = """Please pass auth_token when instantiating the REST API Client or set the environment variable `TELAPI_AUTH_TOKEN`.\
        An auth token is 32 characters long."""
        RestError.__init__(self, message)

class RequestError(RestError):
    pass
