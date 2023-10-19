class RateLimitSignal:
    def __init__(self):
        self.value = False

    def set_true(self) -> None:
        self.value = True

    def set_false(self) -> None:
        self.value = False

    def __bool__(self) -> bool:
        return self.value


class PrivateProfileSignal:
    """ Сигнал оповещающий о том, что профиль приватный. """


class PageLockedOrDeletedSignal:
    """ Сигнал оповещающий о том, что профиль заблокирован, либо удален. """


class AuthorizationFailedSignal:
    """ Сигнал оповещающий о том, что токен невалиден. """


__all__ = [
    'RateLimitSignal',
    'PrivateProfileSignal',
    'PageLockedOrDeletedSignal',
    'AuthorizationFailedSignal',
]
