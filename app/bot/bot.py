import logging

import psycopg_pool
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.bot.handlers.admin import admin_router
from app.bot.handlers.others import others_router
from app.bot.handlers.settings import settings_router
from app.bot.handlers.user import user_router
from app.bot.i18n.translator import get_translations
from app.bot.middlewares.database import DatabaseMiddleware
from app.bot.middlewares.i18n import TranslatorMiddleware
from app.bot.middlewares.lang_settings import LangSettingsMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware
from app.infrastructure.database.connection import get_pg_pool
from config.config import Config
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

async def main(config: Config) -> None:
    logger.info('Starting bot')

    storage = RedisStorage(
        redis=Redis(
            host=config.redis.host,
            port=config.redis.port, 
            db=config.redis.db,
            password=config.redis.password,
            username=config.redis.username,
            )
    )

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    dp = Dispatcher(storage=storage)

    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )

    translations = get_translations()
    locales = list(translations.keys())

    logger.info('Including routers...')
    dp.include_routers(settings_router, admin_router, user_router, others_router)

    logger.info('Including middlewares...')
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(ActivityCounterMiddleware())
    dp.update.middleware(LangSettingsMiddleware())
    dp.update.middleware(TranslatorMiddleware())

    try:
        await dp.start_polling(
            bot, 
            db_pool=db_pool,
            translations=translations,
            locales=locales,
            admin_ids=config.bot.admin_ids
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await db_pool.close()
        logger.info("Connection to Postgres closed")