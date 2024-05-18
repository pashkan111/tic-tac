from src.logic.entities.messages import MessageStatus, Player, PlayerConnected, PlayerConnectedMessage
from src.mappers.publish_mapper import convert_dataclass_to_dict


def test_convert_dataclass_to_dict():
    player = Player(id=1, chip=None)
    message = PlayerConnectedMessage(data=PlayerConnected(player=player), player_sent=Player(id=12, chip=None))

    result = convert_dataclass_to_dict(message)
    assert result == {
        "data": '{"player":{"id":1,"chip":null}}',
        "message_status": MessageStatus.CONNECTED,
        "player_sent": '{"id":12,"chip":null}',
    }
