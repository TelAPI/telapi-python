class RestError(Exception):
    def __init__(self, message, error_code=None, http_code=None):
        Exception.__init__(self, message)
        self.message    = message
        self.error_code = error_code
        self.http_code  = http_code

class AccountSidError(RestError):
    message = "Please pass account_sid when instantiating the REST API Client or set the environment variable `TELAPI_ACCOUNT_SID`.\
        An account SID is a 34 character string that starts with the letters 'AC'."

class AuthTokenError(RestError):
    message = "Please pass auth_token when instantiating the REST API Client or set the environment variable `TELAPI_AUTH_TOKEN`.\
        An auth token is 32 characters long."

class RequestError(RestError):
    pass
