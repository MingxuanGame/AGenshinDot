from typing import Optional
from asyncio import Semaphore

from loguru import logger
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class Database:
    def __init__(self, db_url: str, **kwargs) -> None:
        self.engine = create_async_engine(db_url, **kwargs)
        self.mu = Semaphore(1) if db_url.startswith("sqlite") else None

    async def execute(self, sql: str, **kwargs) -> CursorResult:
        async with AsyncSession(self.engine) as session:
            try:
                if self.mu:
                    await self.mu.acquire()
                result = await session.execute(sql, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                if self.mu:
                    self.mu.release()

    async def close(self) -> None:
        await self.engine.dispose()


db: Optional[Database] = None


def init_db(db_url: str, echo: bool = False, **kwargs) -> None:
    global db

    db = Database(db_url, echo=echo, **kwargs)
    logger.success("数据库初始化完成")


def get_db() -> Optional[Database]:
    return db


async def close() -> None:
    global db

    if db:
        await db.close()
        db = None
        logger.info("数据库已关闭")
