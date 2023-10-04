class ValidationPassed:
    def __new__(cls):
        return True


class ValidationFailed:
    def __new__(cls):
        return False
