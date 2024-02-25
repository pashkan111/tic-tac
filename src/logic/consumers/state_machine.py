"""
У игры несколько состояний
1) Игра начата
2) Сделан ход
3) Победа
"""
from src.logic.events.events import MoveEventData, StartGameEventData, BaseEvent, ClientEventType
from src.logic.exceptions import (
    StateValidationExceptions,
    RoomNotFoundInRepoException,
    UserNotFoundException,
    InvalidTokenException,
)
from src.logic.auth.authentication import check_user
from src.logic.game.game import Game
from src.logic.game.schemas import PlayerId

from dataclasses import dataclass
from typing import Any
from enum import StrEnum
from src.logic.game.main import create_game
from uuid import UUID
from src.logic.game.checker import CheckResult


class MachineActionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(slots=True)
class BaseMachineRequest:
    room_id: UUID
    event: BaseEvent
    player_id: PlayerId | None = None
    game: Game | None = None

    @property
    def data(self):
        return self.event.data


@dataclass(slots=True)
class BaseMachineResponse:
    data: Any
    message: str | None
    status: MachineActionStatus


@dataclass(slots=True)
class StartGameStateData:
    game: Game
    player_id: PlayerId


@dataclass(slots=True)
class MadeMoveStateData:
    move_result: CheckResult


class BaseState:
    next_state: "BaseState"

    def __init__(self, next_state: "BaseState" = None):
        self.next_state = next_state

    def _validate(self, *args, **kwargs):
        ...

    async def run(self, *args, **kwargs) -> BaseMachineResponse:
        ...


# GAME


class GameBaseState(BaseState):
    client_type: ClientEventType | None

    def _validate(self, data: BaseMachineRequest) -> None:
        if data.event.event_type != self.client_type:
            raise StateValidationExceptions(event_type=data.event.event_type, expecting_event_type=self.client_type)


class StartState(GameBaseState):
    client_type = ClientEventType.START

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        self._validate(data)
        event: StartGameEventData = data.event.data
        try:
            player_id = await check_user(event.token)
        except (InvalidTokenException, UserNotFoundException) as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        try:
            game = await create_game(room_id=data.room_id)
        except RoomNotFoundInRepoException as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        self.game = game
        return BaseMachineResponse(
            data=StartGameStateData(game=game, player_id=player_id), status=MachineActionStatus.SUCCESS, message=None
        )


class MoveState(GameBaseState):
    client_type = ClientEventType.MOVE

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        self._validate(data)
        event: MoveEventData = data.event.data
        try:
            move_result = await data.game.make_move(col=event.col, row=event.row, player_id=data.player_id)
            return BaseMachineResponse(
                data=MadeMoveStateData(move_result=move_result), status=MachineActionStatus.SUCCESS, message=None
            )

        except Exception as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))


class SurrenderState(GameBaseState):
    client_type = ClientEventType.SURRENDER


class FinishedState(GameBaseState):
    client_type = None

    def _validate(self, *args, **kwargs):
        pass


class GameStateMachine:
    _states = [StartState, MoveState, SurrenderState, FinishedState]
    current_state: BaseState
    initialized: bool = False

    def __init__(self):
        self._add_states(self._states)

    def _add_states(self, states: list[type[BaseState]]):
        if self.initialized:
            raise ValueError("StateMachine already initialized")
        if not states:
            raise ValueError("States list is empty")
        previous_state = None
        for state in states[::-1]:
            current_state = state(next_state=previous_state)
            previous_state = current_state

        self.current_state = current_state
        self.initialized = True

    async def handle_event(self, data: BaseMachineRequest) -> BaseMachineResponse:
        return await self.current_state.run(data=data)

    def next(self):
        self.current_state = self.current_state.next_state
