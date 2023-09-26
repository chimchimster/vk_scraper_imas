import enum


@enum.unique
class ErrorCodes(enum.Enum):
    """ Handles all exceptions from vkapi. """

    HTTP_ERROR = -1
    UNKNOWN_ERROR = 1
    APP_IS_TURNED_OFF = 2
    UNKNOWN_METHOD_PASSED = 3
    AUTHORIZATION_FAILED = 5
    TOO_MANY_REQUESTS = 6
    INCORRECT_QUERY = 8
    TOO_MANY_ACTIONS = 9
    BAD_GATEWAY = 10
    CAPTCHA_REQUIRED = 14
    PERMISSION_DENIED = 15
    PAGE_LOCKED_OR_DELETED = 18
    API_METHOD_DISABLED = 23
    REACHED_RATE_LIMIT = 29
    MISTAKE_IN_PARAMETER = 100
    USER_IDENTIFIER_ERROR = 113
    ALBUM_PERMISSION_DENIED = 200
    ANONYMOUS_TOKEN_IS_INVALID = 1116

    def __str__(self):
        return f'{self.__dict__.get("_name_")}'


class VKAPIException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        return f'error code {self.error_code} -> {ErrorCodes(self.error_code)}'