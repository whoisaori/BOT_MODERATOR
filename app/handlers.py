import re

from typing import Any

from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from pymorphy3 import MorphAnalyzer  # Морфологический анализатор

from contextlib import suppress
from datetime import datetime, timedelta

from app.filters import BotMessage, GroupMessage
from app.banwords import banwords as bs
from app.generators import gpt4

router = Router()

morph = MorphAnalyzer(lang='ru')


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None

    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    current_datetime = datetime.now()

    if match_:
        value, unit = int(match_.group(1)), match_.group(2)

        match unit:
            case 's': time_delta = timedelta(seconds=value)
            case 'm': time_delta = timedelta(minutes=value)
            case 'h': time_delta = timedelta(hours=value)
            case 'd': time_delta = timedelta(days=value)
            case 'w': time_delta = timedelta(weeks=value)
            case _: return None
    else:
        return None

    new_datetime = current_datetime + time_delta

    return new_datetime


class Generate(StatesGroup):
    text = State()


@router.message(CommandStart(), BotMessage())
async def process_start_command(message: Message):
    await message.answer("Привет! Добавь меня в чат и " +
                         "укажи мне ID этого чата для дальнейшей работы.")


@router.message(Command('get_chat_id'))
async def get_chat_id(message: Message, state: FSMContext):
    await message.reply(parse_mode="HTML",
                        text=f"<b>ID чата:</b> {message.chat.id}")
    await state.clear()


@router.message(Command('ban'), GroupMessage())
async def ban(message: Message, command: CommandObject):
    reply = message.reply_to_message

    if not reply:
        return await message.answer("👀 Пользователь не найден!")

    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
        )
        if member.status not in ['creator', 'administrator']:
            await message.bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=reply.from_user.id,
                until_date=until_date,
            )
            await message.answer(f"😱 Пользователя <b>{mention}</b> забанили до " +
                                 f"{until_date.strftime('%H:%M %d/%B/%Y')}!")
        else:
            await message.reply("😶‍🌫️ Таких нам банить нельзя!")


@router.message(Command('mute'), GroupMessage())
async def mute(message: Message, command: CommandObject):
    reply = message.reply_to_message

    if not reply:
        return await message.answer("👀 Пользователь не найден!")

    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.username)

    with suppress(TelegramBadRequest):
        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
        )
        if member.status not in ['creator', 'administrator']:
            await message.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=reply.from_user.id,
                until_date=until_date,
                permissions=ChatPermissions(can_send_messages=False),
            )
            await message.answer(f"🤐 Пользователя <b>{mention}</b> замутили до " +
                                 f"{until_date.strftime('%H:%M %d/%B/%Y')}!")
        else:
            await message.reply("😶‍🌫️ Таких нам мутить нельзя!")


@router.message(Generate.text)
async def generate_eror(message: Message):
    await message.answer("Подождите... GPT всё ещё пытается вам ответить...")


@router.message(Command('gpt'))
async def gpt_response(message: Message,
                       command: CommandObject,
                       state: FSMContext):
    await state.set_state(Generate.text)
    response = await gpt4(command.args)
    print(response)
    await message.answer(response.choices[0].message.content)
    await state.clear()


@router.message(F.text, GroupMessage())
async def echo_message(message: Message) -> Any:
    """Обработчик банвордов"""
    for word in message.text.lower().strip().split():
        parsed_word = morph.parse(word)[0]
        normal_form = parsed_word.normal_form

        for banword in bs:
            if banword.lower().strip() in normal_form:
                await message.delete()
                return await message.answer(f"🤬 @{message.from_user.username} не ругайся!")
