from python_tools.redis_tools.redis_client import RedisClient
import settings
from src.logic.events.messages import BaseMessage
from fastapi.websockets import WebSocket
from logging import getLogger
import uuid


logger = getLogger(__name__)
redis_client = RedisClient(settings.REDIS_CONNECTION_STRING)


async def publish_message(*, channel: str, message: BaseMessage):
    await redis_client.get().xadd(channel=channel, data=message.to_dict())


async def read_messages(*, room_id: uuid.UUID, websocket: WebSocket):
    channel = get_channel_name(room_id)
    last_id = "0-0"
    while True:
        message = await redis_client.get().xread(streams={channel: last_id}, count=5, block=5)
        if message:
            logger.info(message)
            last_id = message[0][1][-1][0]
            message_text = message[0][1][-1][1]


def get_channel_name(room_id: uuid.UUID) -> str:
    return f"{settings.REDIS_CHANNEL_FOR_NOTIFICATIONS}:{str(room_id)}"
