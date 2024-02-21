class AbstractException(Exception):
    message: str

    def __init__(self, msg: str | None = None, **kwargs):
        message = self.message or msg
        self.message = message.format(**kwargs)
        super().__init__(self.message)


class ChipDoesNotExistsException(AbstractException):
    message = "Chip {chip} Does Not Exists"


class MakeMoveException(AbstractException):
    message = "Error making move. Row={row}, col={col}"


class RowsNumberException(AbstractException):
    message = "Wrong Rows count. Max: {max_rows}, Min: {min_rows}"


class PlayersNotEnoughException(AbstractException):
    message = "Players Not Enough. Room id: {room_id}"


class GameNotStartedException(AbstractException):
    message = "Game not started. Call start() func. Room id: {room_id}"


class NotEnoughArgsException(AbstractException):
    message = "Not Enough Args. Args: {args}"

    def __init__(self, **args):
        args_to_message = ""
        for k, v in args.items():
            args_to_message += f"{k}={str(v)}; "
        self.message = self.message.format(args=args_to_message)
        super().__init__(self.message)


class RoomNotFoundInRepoException(AbstractException):
    message = "Room Not Found In Repo. Room id: {room_id}"


class PartnerDoesNotExistsException(AbstractException):
    message = "Game has not been created. There is no partner for this player. Room id: {room_id}"


class BadParamsException(AbstractException):
    message = "Bad Params. Params: {params}"

    def __init__(self, **params):
        params_to_message = ""
        for k, v in params.items():
            params_to_message += f"{k}={str(v)}; "
        self.message = self.message.format(params=params_to_message).strip()
        super().__init__(self.message)


class InvalidTokenException(AbstractException):
    message = "Invalid Token. Token: {token}"


class UserNotFoundException(AbstractException):
    message = "User Not Found. User id: {user_id}"


class UserInvalidCredsException(AbstractException):
    message = "Invalid Credentials. Username: {username}"


class MoveTurnException(AbstractException):
    message = "Others players turn to move. Player id: {player_id}"


class StateValidationExceptions(AbstractException):
    message = "Wrong event type. Event type: {event_type}, expecting: {expecting_event_type}"
