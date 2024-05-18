"""
У игры несколько состояний
1) Игра начата
2) Сделан ход
3) Победа
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable
from uuid import UUID

from src.logic.auth.authentication import check_user
from src.logic.entities.events import BaseEvent, ClientEventType, MoveEventData, StartGameEventData
from src.logic.exceptions import (
    InvalidTokenException,
    RoomNotFoundInRepoException,
    StateValidationException,
    TokenExpiredException,
    UserNotFoundException,
)
from src.logic.game.checker import CheckResult
from src.logic.game.game import Game
from src.logic.game.main import create_game
from src.logic.game.player import Player
from src.logic.game.schemas import PlayerId


class MachineActionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(slots=True)
class BaseMachineRequest:
    room_id: UUID
    event: BaseEvent
    player_id: PlayerId | None = None
    game: Game | None = None


@dataclass(slots=True)
class BaseMachineResponse:
    data: Any
    message: str | None
    status: MachineActionStatus


@dataclass(slots=True)
class StartGameStateData:
    game: Game
    player: Player


@dataclass(slots=True)
class MadeMoveStateData:
    move_result: CheckResult


@dataclass(slots=True)
class SurrenderStateData:
    winner: Player


class GameState(StrEnum):
    NEW_STATE = "NEW_STATE"
    START_STATE = "START_STATE"
    MOVE_STATE = "MOVE_STATE"
    FINISHED_STATE = "FINISHED_STATE"
    SURRENDER_STATE = "SURRENDER_STATE"


_EVENTS_MAPPING = {
    ClientEventType.START: GameState.START_STATE,
    ClientEventType.MOVE: GameState.MOVE_STATE,
    ClientEventType.SURRENDER: GameState.SURRENDER_STATE,
}


def get_game_state(client_state: ClientEventType) -> GameState:
    return _EVENTS_MAPPING[client_state]


# GAME
class GameBaseState:
    client_type: ClientEventType | None
    state_name: GameState
    next_states: list["GameState"]

    def _validate(self, data: BaseMachineRequest) -> None:
        if data.event.event_type != self.client_type:
            raise StateValidationException(event_type=data.event.event_type, expecting_event_type=self.client_type)

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        ...


class NewState(GameBaseState):
    client_type = None
    state_name = GameState.NEW_STATE
    next_states = [GameState.START_STATE]

    def _validate(self, data: BaseMachineRequest) -> None:
        ...


class StartState(GameBaseState):
    client_type = ClientEventType.START
    state_name = GameState.START_STATE
    next_states = [GameState.MOVE_STATE, GameState.SURRENDER_STATE, GameState.FINISHED_STATE]

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        try:
            self._validate(data)
        except StateValidationException as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        event: StartGameEventData = data.event.data
        try:
            player_id = await check_user(event.token)
        except (InvalidTokenException, UserNotFoundException, TokenExpiredException) as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        try:
            game = await create_game(room_id=data.room_id)
        except RoomNotFoundInRepoException as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        return BaseMachineResponse(
            data=StartGameStateData(game=game, player=game.get_player_by_id(player_id)),
            status=MachineActionStatus.SUCCESS,
            message=None,
        )


class MoveState(GameBaseState):
    client_type = ClientEventType.MOVE
    state_name = GameState.MOVE_STATE
    next_states = [GameState.FINISHED_STATE, GameState.SURRENDER_STATE]

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        try:
            self._validate(data)
        except StateValidationException as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

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
    state_name = GameState.SURRENDER_STATE
    next_states = []

    async def run(self, data: BaseMachineRequest) -> BaseMachineResponse:
        try:
            self._validate(data)
        except StateValidationException as e:
            return BaseMachineResponse(data=None, status=MachineActionStatus.FAILED, message=str(e))

        winner = list(filter(lambda p: p.id != data.player_id, data.game.players))[0]
        # TODO come up with idea how get a winner without this shit
        await data.game.finish(winner)
        return BaseMachineResponse(
            data=SurrenderStateData(winner=winner),
            status=MachineActionStatus.SUCCESS,
            message=None,
        )


class FinishedState(GameBaseState):
    client_type = None
    state_name = GameState.FINISHED_STATE
    next_states = [GameState.FINISHED_STATE]

    def _validate(self, *args, **kwargs):
        pass


class GameStateMachine:
    current_state: GameBaseState = NewState()

    async def handle_event(self, data: BaseMachineRequest) -> BaseMachineResponse:
        return await self.current_state.run(data=data)

    def can_change_state(self, state: GameState) -> bool:
        return state in self.current_state.next_states or state == self.current_state.state_name

    def change_state(self, state: GameState):
        if self.current_state.state_name == state:
            return

        state_method = _get_state_method(state_machine=self, state=state)
        state_method()

    def _start_state(self):
        self.current_state = StartState()

    def _move_state(self):
        if not GameState.MOVE_STATE in self.current_state.next_states:
            raise StateValidationException
        self.current_state = MoveState()

    def _surrender_state(self):
        if not GameState.SURRENDER_STATE in self.current_state.next_states:
            raise StateValidationException
        self.current_state = SurrenderState()

    def _finished_state(self):
        if not GameState.FINISHED_STATE in self.current_state.next_states:
            raise StateValidationException
        self.current_state = FinishedState()


def _get_state_method(*, state: GameState, state_machine: GameStateMachine) -> Callable:
    return getattr(state_machine, f"_{state.lower()}")
