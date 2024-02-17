from src.logic.game.board import BoardArray
from src.logic.game.checker import CheckerArray
from src.repo.repository_game import RepositoryGame
from src.logic.game.player import Player
from src.logic.interfaces import Chips
import pytest
from unittest.mock import Mock


@pytest.fixture()
def player1_fixture() -> Player:
    return Player(id=10, chip=Chips.O)


@pytest.fixture()
def player2_fixture() -> Player:
    return Player(id=20, chip=Chips.X)


@pytest.fixture()
def board_fixture() -> BoardArray:
    return BoardArray(rows_count=5)


@pytest.fixture()
def repo_fixture() -> RepositoryGame:
    return Mock(spec=RepositoryGame)


@pytest.fixture()
def checker_fixture() -> CheckerArray:
    return CheckerArray()
