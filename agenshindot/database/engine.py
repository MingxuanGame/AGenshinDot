from __future__ import annotations

from asyncio import Semaphore
from typing import Any, TypeVar, Iterable, Optional

from loguru import logger
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import delete, insert, select, update, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()
TBase = TypeVar("TBase", bound=Base)


class Database:
    def __init__(self, db_url: str, **kwargs: Any) -> None:
        self.engine = create_async_engine(db_url, **kwargs)
        self.session = AsyncSession(bind=self.engine)
        self.mu = Semaphore(1) if db_url.startswith("sqlite") else None

    async def execute(self, sql: str, **kwargs) -> CursorResult:
        try:
            if self.mu:
                await self.mu.acquire()
            result = await self.session.execute(sql, **kwargs)
            await self.session.commit()
            return result
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            if self.mu:
                self.mu.release()

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def insert(self, table: type[TBase], **data: Any) -> None:
        await self.execute(insert(table).values(**data))

    async def delete(self, table: type[TBase], *condition) -> None:
        await self.execute(delete(table).where(*condition))

    async def update(
        self, table: type[TBase], *condition, **data: Any
    ) -> None:
        await self.execute(update(table).where(*condition).values(**data))

    async def select(
        self, table: type[TBase], primary_key: int, **kwargs: Any
    ) -> Optional[TBase]:
        return await self.session.get(table, primary_key, **kwargs)

    async def fetch(self, table: type[TBase], *condition) -> Iterable[TBase]:
        return (await self.execute(select(table).where(*condition))).scalars()

    async def close(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    # Complex API

    async def insert_or_update(
        self, table: type[TBase], primary_key: int, **data: Any
    ) -> bool:
        if await self.select(table, primary_key):
            await self.update(
                table, inspect(table).primary_key[0] == primary_key, **data
            )
            return False
        else:
            await self.insert(table, **data)
            return True

    async def insert_or_ignore(
        self, table: type[TBase], primary_key: int, **data: Any
    ) -> bool:
        if not (await self.select(table, primary_key)):
            await self.insert(table, **data)
            return True
        return False


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
