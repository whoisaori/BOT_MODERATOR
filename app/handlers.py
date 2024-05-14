from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from app.filters import BotMessage, GroupMessage
from banwords import banwords as bs

router = Router()


@router.message(CommandStart(), BotMessage())
async def process_start_command(message: Message):
    await message.answer("Привет! Добавь меня в чат и " +
                         "укажи мне ID этого чата для дальнейшей работы.")


@router.message(Command(commands=['get_chat_id']))
async def get_chat_id(message: Message):
    await message.reply(parse_mode="HTML",
                        text=f"<b>ID чата:</b> {message.chat.id}")


@router.message(GroupMessage())
async def echo_message(message: Message):
    """Обработчик банвордов"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    chat_member = await message.bot.get_chat_member(chat_id=chat_id,
                                                    user_id=user_id)

    for word in bs:
        if word.lower() in message.text.lower():
            if chat_member.status != 'creator' and chat_member.status != 'administrator':
                await message.bot.delete_message(chat_id=message.chat.id,
                                                 message_id=message.message_id)
                if not username:
                    await message.bot.send_message(chat_id=message.chat.id,
                                                   text=f"{message.from_user.first_name} - такое нельзя писать 🤬",
                                                   parse_mode="HTML")
                await message.bot.send_message(chat_id=message.chat.id,
                                               text=f"@{username} - такое нельзя писать 🤬",
                                               parse_mode="HTML")
