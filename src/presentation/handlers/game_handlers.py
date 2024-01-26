from fastapi import APIRouter, exceptions
from src.presentation.entities.game_entities import GameStartRequest, GameStartResponse
from src.logic.game.main import create_game
from src.logic.auth.authentication import check_user
from src.logic.exceptions import (
    NotEnoughArgsException,
    RoomNotFoundInRepoException,
    PlayersNotEnoughException,
)


game_router = APIRouter(prefix="/game")


@game_router.post("/create", response_model=GameStartResponse)
async def create_game_handler(data: GameStartRequest):
    try:
        user_id = await check_user(data.token)
    except:
        raise exceptions.HTTPException(status_code=401)

    try:
        game = await create_game(player_id=user_id, rows_count=data.rows_count)
    except (RoomNotFoundInRepoException, NotEnoughArgsException) as exc:
        raise exceptions.HTTPException(status_code=400, detail=exc.message)
    except PlayersNotEnoughException:
        return GameStartResponse(game_started=False, room_id=None, partner_id=None)
    except Exception as exc:
        return GameStartResponse(game_started=False, room_id=None, partner_id=None)

    return GameStartResponse(
        game_started=True,
        partner_id=[player.id for player in game.players if player.id != user_id][0],
        room_id=game.room_id,
    )
