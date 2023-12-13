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


class RowsNumberException(AbstractException):
    message = "Wrong Rows count. Max: {max_rows}, Min: {min_rows}"


class PlayersNotEnoughException(AbstractException):
    message = "Players Not Enough. Room id: {room_id}"


class GameNotStartedException(AbstractException):
    message = "Game not started. Call start() func. Room id: {room_id}"
