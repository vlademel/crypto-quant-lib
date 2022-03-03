class LessThanMinTransactionAmount(Exception):
    pass

class IncryptException(Exception):
    def __init__(self, message):
        self._message = message
        super().__init__(self._message)

    def __str__(self):
        return 'Incrypt -> {message!s}'.format(message=self._message)

    @staticmethod
    def fail(message):
        raise IncryptException(message)

    @staticmethod
    def require(requirement, message):
        if not(requirement):
            raise IncryptException(message)