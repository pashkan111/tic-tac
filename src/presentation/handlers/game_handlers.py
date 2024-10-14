from fastapi import APIRouter, exceptions, status

from src.logic.auth.authentication import check_user
from src.logic.exceptions import (
    NotEnoughArgsException,
    PlayersAlreadyInWaitingListException,
    PlayersNotEnoughException,
    RoomNotFoundInRepoException,
    RowsNumberException,
)
from src.logic.game.main import create_game
from src.logic.game.schemas import Chips
from src.presentation.entities.game_entities import (
    GameStartRequest,
    GameStartResponse,
    PlayerDeleteFromWaitingRequest,
    PlayerDeleteFromWaitingResponse,
    GetUserExistingGameRequest,
    GetUserExistingGameResponse,
)
from src.presentation.entities.get_chips import Chip, GetChipsResponse
from src.repo.repository_game import repo
from src.services.delete_player_from_waiting_list import delete_player_from_waiting_list

game_router = APIRouter(prefix="/game")


@game_router.post("/create", response_model=GameStartResponse)
async def create_game_handler(data: GameStartRequest):
    try:
        user_id = await check_user(data.token)
    except Exception as e:
        raise exceptions.HTTPException(status_code=401, detail=str(e))

    try:
        game = await create_game(player_id=user_id, rows_count=data.rows_count)
    except RowsNumberException as exc:
        raise exceptions.HTTPException(status_code=400, detail=exc.message)
    except (RoomNotFoundInRepoException, NotEnoughArgsException) as exc:
        raise exceptions.HTTPException(status_code=400, detail=exc.message)
    except (PlayersNotEnoughException, PlayersAlreadyInWaitingListException):
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
async def get_chips_handler():
    return GetChipsResponse(chips=[Chip(id=chip.value, chip=chip.name) for chip in Chips])


@game_router.post(
    "/delete-player-from-waiting-list",
    status_code=status.HTTP_200_OK,
    response_model=PlayerDeleteFromWaitingResponse,
)
async def delete_player_from_waiting_list_handler(data: PlayerDeleteFromWaitingRequest):
    deleted = await delete_player_from_waiting_list(data.rows_count)
    return PlayerDeleteFromWaitingResponse(deleted=deleted)


@game_router.post("/get-existing-game", response_model=GetUserExistingGameResponse)
async def get_existing_game_handler(data: GetUserExistingGameRequest):
    try:
        user_id = await check_user(data.token)
    except Exception as e:
        raise exceptions.HTTPException(status_code=401, detail=str(e))

    existing_game_id = await repo.get_player_active_game(user_id)
    return GetUserExistingGameResponse(game_id=existing_game_id)
