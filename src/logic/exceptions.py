class AbstractException(Exception):
    message: str
    def __init__(self, msg: str | None = None, **kwargs):
        message = self.message or msg
        self.message = message.format(**kwargs)
        super().__init__(self.message)


class ChipDoesNotExistsException(AbstractException):
    message = "Chip {chip} Does Not Exists"


class MakeMoveException(AbstractException):
    message = "it is not possible to make move. Row={row}, col={col}"