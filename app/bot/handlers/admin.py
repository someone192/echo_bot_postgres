import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import UserRoleFilter
from app.infrastructure.database.db import (
    change_user_banned_status_by_id,
    change_user_banned_status_by_username,
    get_statistics,
    get_user_banned_status_by_id,
    get_user_banned_status_by_username,
)
from psycopg import AsyncConnection

logger = logging.get_logger(__name__)

admin_router = Router()

admin_router.message.filter(UserRoleFilter(UserRole.ADMIN))

#Handler for command "help" from user with role 'UserRole.ADMIN'
@admin_router.message(Command('help'))
async def process_admin_help_command(message: Message, i18n: dict):
    await message.answer(text=i18n.get('/help_admin'))

#Handler for command "statistics" from user with role 'UserRole.ADMIN'
@admin_router.message(Command('/statistics'))
async def process_admin_statistics_command(message: Message, conn: AsyncConnection, i18n: dict[str, str]):
    statistics = await get_statistics(conn)
    await message.answer(
        text=i18n.get('statistics').format(
            "/n".join(
                f"{i}. <b>{stat[0]}</b>: {stat[1]}"
                for i,stat in enumerate(statistics,1)
            )
        )
    )

#Handler for command "ban" from user with role 'UserRole.ADMIN'
@admin_router.message(Command('ban'))
async def process_admin_ban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str]
)-> None:
    args = command.args

    if not args:
        await message.reply(i18n.get('empty_bad_answer'))
        return
    
    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(conn, user_id=arg_user[1:])
    else:
        await message.answer(text=i18n.get('incorrect_ban_arg'))
        return
    
    if banned_status is None:
        await message.answer(i18n.get('no_user'))
    elif banned_status:
        await message.reply(i18n.get('already_banned'))
    else:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(conn, user_id=int(arg_user), banned=True)
        else:
            await change_user_banned_status_by_username(conn, username=arg_user[1:], banned=True)
        await message.reply(text=i18n.get('successfully_banned'))

#Handler for commmand "unban" from user with role "UserRole.ADMIN"
@admin_router.message(Command('unban'))
async def process_admin_unban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str]
)-> None:
    args = command.args

    if not args:
        await message.reply(i18n.get('empty_bad_answer'))
        return
    
    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(conn, user_id=arg_user[1:])
    else:
        await message.answer(text=i18n.get('incorrect_unban_arg'))
        return
    
    if banned_status is None:
        await message.answer(i18n.get('no_user'))
    elif banned_status:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(conn, user_id=int(arg_user), banned=False)
        else:
            await change_user_banned_status_by_username(conn, username=arg_user[1:], banned=False)
        await message.reply(text=i18n.get('successfully_unbanned'))
    else:
        await message.reply(i18n.get('already_unbanned'))