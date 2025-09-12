import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, Update, User

logger = logging.getLogger(__name__)

class LangSettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
    ) -> Any:
        logger.debug('lang_settings_middleware')
        user: User = data.get('event_from_user')
        logger.debug('user is ready')
        if user is None:
            logger.debug('user is None')
            return await handler(event, data)
        
        if event.callback_query is None:
            logger.debug('event is None')
            return await handler(event, data)
        
        logger.debug('locales')
        locales: list[str] = data.get('locales')
        logger.debug('locales are ready')

        logger.debug('state')
        state: FSMContext = data.get('state')
        logger.debug('state is ready')
        user_context_data = await state.get_data()
        logger.debug('context_data is ready')

        if event.callback_query.data == 'cancel_lang_button_data':
            logger.debug('cancel btn')
            user_context_data.update(user_lang = None)
            logger.debug('context data is ready')
            await state.set_data(user_context_data)

        elif event.callback_query.data in locales and event.callback_query.data != user_context_data.get('user_lang'):
            logger.debug('changed lang')
            user_context_data.update(user_lang=event.callback_query.data)
            logger.debug('changed_lang_context')
            await state.set_data(user_context_data)
        
        logger.debug('exit lang settings middleware')
        return await handler(event, data)