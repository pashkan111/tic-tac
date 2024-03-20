from fastapi import APIRouter, exceptions
from src.presentation.entities.game_entities import GameStartRequest, GameStartResponse
from src.presentation.entities.get_chips import GetChipsResponse, Chip
from src.logic.game.main import create_game
from src.logic.auth.authentication import check_user
from src.logic.exceptions import (
    NotEnoughArgsException,
    RoomNotFoundInRepoException,
    PlayersNotEnoughException,
)
from src.logic.game.schemas import Chips

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
        return GameStartResponse(game_started=False, room_id=None, partner_id=None, added_to_queue=True)
    except Exception as exc:
        raise exceptions.HTTPException(status_code=500, detail=exc)

    return GameStartResponse(
        game_started=True,
        partner_id=[player.id for player in game.players if player.id != user_id][0],
        room_id=game.room_id,
        added_to_queue=False,
    )


@game_router.get("/chips", response_model=GetChipsResponse)
async def get_chips():
    return GetChipsResponse(chips=[Chip(id=chip.value, chip=chip.name) for chip in Chips])
