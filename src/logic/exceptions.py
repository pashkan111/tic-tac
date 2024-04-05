class AbstractException(Exception):
    message: str

    def __init__(self, msg: str | None = None, **kwargs):
        message = self.message or msg
        self.message = message.format(**kwargs)
        super().__init__(self.message)


class ServerException(AbstractException):
    message = "Server Exception. {message}"


class ChipDoesNotExistsException(AbstractException):
    message = "Chip {chip} Does Not Exists"


class MakeMoveException(AbstractException):
    message = "Error making move. Row={row}, col={col}"


class RowsNumberException(AbstractException):
    message = "Wrong Rows count. Max: {max_rows}, Min: {min_rows}"


class PlayersNotEnoughException(AbstractException):
    message = "Players Not Enough. Room id: {room_id}"


class PlayersAlreadyInWaitingListException(AbstractException):
    message = "Player already is in waiting list. Rows count: {rows_count}"


class GameNotActiveException(AbstractException):
    message = "Game is not active. Room id: {room_id}"


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


class BadEventParamsException(AbstractException):
    message = "Bad Params. Current params: [{current_params}]. Needed params: [{needed_params}]"

    def __init__(self, current_params: list[str], needed_params: list[str]):
        current_params_text = ", ".join([f'"{param}"' for param in current_params])
        needed_params_text = ", ".join([f'"{param}"' for param in needed_params])
        self.message = self.message.format(current_params=current_params_text, needed_params=needed_params_text).strip(
            "; "
        )


class BadEventTypeException(AbstractException):
    message = "Event '{event}' does not exist"


# AUTH EXCEPTIONS
# ________________________________________________________________
class InvalidTokenException(AbstractException):
    message = "Invalid Token. Token: {token}"


class TokenExpiredException(AbstractException):
    message = "Token Expired"


class UserNotFoundException(AbstractException):
    message = "User Not Found. User id: {user_id}"


class UserInvalidCredsException(AbstractException):
    message = "User with username {username} does not exist"


class UserInvalidPasswordException(AbstractException):
    message = "Invalid Password"


class UsernameAlreadyExistsException(AbstractException):
    message = "User with such username already exists. Username: {username}"


# ________________________________________________________________


class MoveTurnException(AbstractException):
    message = "Others players turn to move. Player id: {player_id}"


class StateValidationException(AbstractException):
    message = "Wrong event type. Event type: {event_type}, expecting: {expecting_event_type}"
