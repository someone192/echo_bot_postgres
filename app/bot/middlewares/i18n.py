import logging 
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from aiogram.fsm.context import FSMContext
from psycopg import AsyncConnection
from app.infrastructure.database.db import get_user_lang

logger = logging.getLogger(__name__)

class TranslatorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        logger.debug('translator_middleware')
        user: User = data.get("event_from_user")
        logger.debug('user is ready')

        if user is None:
            logger.debug('user is None')
            return await handler(event, data)
        
        
        state: FSMContext = data.get('state')
        logger.debug('state is ready')
        user_context_data = await state.get_data()
        logger.debug('user_context_data is ready')

        if (user_lang := user_context_data.get('user_lang')) is None:
            logger.debug('user_lang is None')

            conn: AsyncConnection = data.get('conn')
            logger.debug('conn is ready')
            if conn is None:
                logger.error('Database connection not found in midlleware data')
                raise RuntimeError("Missing database connection for detecting the user`s language")
            
            user_lang: str | None = await get_user_lang(conn, user_id=user.id)
            logger.debug('user_lang is ready')
            if user_lang is None:
                user_lang = user.language_code
                logger.debug('user_lang is None')

        translations: dict = data.get('translations')
        logger.debug('translations are ready')
        i18n: dict = translations.get('user_lang')
        logger.debug('i18n is ready')

        if i18n is None:
            data['i18n'] = translations[translations['default']]
            logger.debug(data['i18n'])
        else:
            data['i18n'] = i18n
            logger.debug('data i18n is ready')

        return await handler(event, data)