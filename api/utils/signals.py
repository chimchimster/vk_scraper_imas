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
    pass


__all__ = [
    'RateLimitSignal',
    'PrivateProfileSignal'
]
