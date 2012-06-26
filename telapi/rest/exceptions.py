class RestError(Exception):
    pass

class AccountSidError(RestError):
    message = "Please pass account_sid when instantiating the REST API Client or set the environment variable `TELAPI_ACCOUNT_SID`.\
        An account SID is a 34 character string that starts with the letters 'AC'."

class AuthTokenError(RestError):
    message = "Please pass auth_token when instantiating the REST API Client or set the environment variable `TELAPI_AUTH_TOKEN`.\
        An auth token is 32 characters long."

class RequestError(RestError):
    pass
