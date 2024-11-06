import logging
from typing import AsyncGenerator

from config import settings
from loguru import logger
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


engine = create_async_engine(settings.DB_URL, echo=True)

logging.basicConfig(handlers=[InterceptHandler()], level=0)
logging.getLogger("db.engine").setLevel(logging.DEBUG)


async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            logger.debug('Try yield session')
            return session
        except:
            logger.debug('Session rollback')
            await session.rollback()
            raise
        finally:
            logger.debug('Session close')
            await session.close()
