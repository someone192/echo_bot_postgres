from aiogram import Router
from aiogram.types import Message
from psycopg import AsyncConnection

others_router = Router()

@others_router.message()
async def send_echo(message: Message, conn: AsyncConnection, i18n: dict):
    try:
        message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=i18n.get('no_echo'))