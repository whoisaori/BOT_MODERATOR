from aiogram.types import Message
from aiogram.filters import Filter

GROUP_ID = "-1002098551625"


class BotMessage(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == 'private'


class GroupMessage(Filter):
    def __init__(self):
        self.group_id = GROUP_ID

    async def __call__(self, message: Message) -> bool:
        return f"{message.chat.id}" == self.group_id
