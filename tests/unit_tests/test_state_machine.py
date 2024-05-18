import uuid

import pytest

from src.logic.entities.events import (
    ClientEventType,
    MoveEvent,
    MoveEventData,
    StartGameEvent,
    StartGameEventData,
    Token,
)
from src.logic.game.game import Game
from src.services.state_machine import (
    BaseMachineRequest,
    BaseMachineResponse,
    GameState,
    GameStateMachine,
    MachineActionStatus,
    NewState,
    StartGameStateData,
    StartState,
)


@pytest.mark.asyncio
async def test_state_machine(mocker, repo_fixture, board_fixture, player1_fixture, player2_fixture, checker_fixture):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    state_machine = GameStateMachine()
    assert type(state_machine.current_state) == NewState

    can_change = state_machine.can_change_state(GameState.START_STATE)
    assert can_change is True

    can_change_err = state_machine.can_change_state(GameState.MOVE_STATE)
    assert can_change_err is False

    state_machine.change_state(GameState.START_STATE)

    move_event = MoveEvent(event_type=ClientEventType.MOVE, data=MoveEventData(row=1, col=1))
    assert await state_machine.handle_event(
        BaseMachineRequest(event=move_event, room_id=game.room_id)
    ) == BaseMachineResponse(
        data=None,
        status=MachineActionStatus.FAILED,
        message="Wrong event type. Event type: MOVE, expecting: START",
    )

    assert type(state_machine.current_state) == StartState

    start_event = StartGameEvent(event_type=ClientEventType.START, data=StartGameEventData(token=Token(uuid.uuid4())))
    mocker.patch("src.services.state_machine.check_user", return_value=player1_fixture.id)
    mocker.patch("src.services.state_machine.create_game", return_value=game)
    state_response = await state_machine.handle_event(BaseMachineRequest(event=start_event, room_id=game.room_id))
    assert state_response == BaseMachineResponse(
        data=StartGameStateData(game=game, player=player1_fixture),
        message=None,
        status=MachineActionStatus.SUCCESS,
    )
