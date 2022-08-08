from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Text, Column, Integer, SmallInteger

from ..engine import Base


class IDOrm(Base):
    __tablename__ = "id"

    qq = Column(Integer, primary_key=True)
    uid = Column(Integer)
    mihoyo_id = Column(Integer)


class CookieOrm(Base):
    __tablename__ = "cookie"

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    cookie = Column(Text)
    times = Column(SmallInteger)


class PublicCookieOrm(Base):
    __tablename__ = "public_cookie"

    id = Column(Integer, primary_key=True, autoincrement=1)
    cookie = Column(Text, nullable=False)
    times = Column(SmallInteger, nullable=False)


class CookieCacheOrm(Base):
    __tablename__ = "cookie_cache"

    uid = Column(Integer, primary_key=True)
    cookie = Column(Text, nullable=False)


class ID(BaseModel):
    qq: int
    uid: Optional[int] = None
    mihoyo_id: Optional[int] = None

    class Config:
        orm_mode = True


class Cookie(BaseModel):
    uid: int
    cookie: Optional[str] = None
    times: Optional[int] = None

    class Config:
        orm_mode = True


class PublicCookie(BaseModel):
    id: int
    cookie: str
    times: int

    class Config:
        orm_mode = True


class CookieCache(BaseModel):
    uid: int
    cookie: str

    class Config:
        orm_mode = True
