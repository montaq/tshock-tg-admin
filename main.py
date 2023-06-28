import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from handlers import default_commands, authorization, main_menu, server_section, users_section
from aiogram.fsm.storage.redis import RedisStorage, Redis
from config.configreader import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from keyboards.default_menu import set_default_menu
from middlewares.db import DbSessionMiddleware
from middlewares.language import UserLanguageMiddleware
from models.methods import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

BOT_TOKEN: str = config.bot_token
redis: Redis = Redis(host='redis')

storage: RedisStorage = RedisStorage(redis=redis)

engine = create_async_engine(config.postgres_dsn, future=True, echo=True)

db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

bot: Bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp: Dispatcher = Dispatcher(storage=storage)

# Allow interaction in private chats (not groups or channels) only
dp.message.filter(F.chat.type == "private")


# Register middlewares
# This middleware fires before filters
dp.message.outer_middleware(DbSessionMiddleware(db_pool))
dp.callback_query.outer_middleware(DbSessionMiddleware(db_pool))
# This middleware fires after filters
dp.message.middleware(UserLanguageMiddleware())
dp.callback_query.middleware(UserLanguageMiddleware())

# Register routers
dp.include_router(default_commands.router)
dp.include_router(authorization.router)
dp.include_router(main_menu.router)
dp.include_router(server_section.router)
dp.include_router(users_section.router)


async def main():
    await create_tables(engine)
    await set_default_menu(bot)  # TODO: rewrite to multilang
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
