from src.logic.consumers.state_machine import (
    GameStateMachine,
    StartState,
    BaseMachineResponse,
    StartGameStateData,
    MachineActionStatus,
    BaseMachineRequest,
)
from src.logic.events.events import StartGameEvent, StartGameEventData, MoveEvent, MoveEventData, ClientEventType, Token
import pytest
from src.logic.game.game import Game
from src.logic.exceptions import StateValidationExceptions
import uuid


@pytest.mark.asyncio
async def test_state_machine(mocker, repo_fixture, board_fixture, player1_fixture, player2_fixture, checker_fixture):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    state_machine = GameStateMachine()
    assert type(state_machine.current_state) == StartState

    move_event = MoveEvent(event_type=ClientEventType.MOVE, data=MoveEventData(row=1, col=1))
    with pytest.raises(StateValidationExceptions):
        await state_machine.handle_event(BaseMachineRequest(event=move_event, room_id=game.room_id))

    start_event = StartGameEvent(event_type=ClientEventType.START, data=StartGameEventData(token=Token(uuid.uuid4())))
    mocker.patch("src.logic.consumers.state_machine.check_user", return_value=player1_fixture.id)
    mocker.patch("src.logic.consumers.state_machine.create_game", return_value=game)
    state_response = await state_machine.handle_event(BaseMachineRequest(event=start_event, room_id=game.room_id))
    assert state_response == BaseMachineResponse(
        data=StartGameStateData(game=game, player_id=player1_fixture.id),
        message=None,
        status=MachineActionStatus.SUCCESS,
    )
