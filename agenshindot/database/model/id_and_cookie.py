from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy import Text, Column, Integer, ForeignKey

from agenshindot.database.engine import Base


class IDOrm(Base):
    __tablename__ = "id"

    qq = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("cookie.uid"))
    mihoyo_id = Column(Integer)

    cookie = relationship("Cookie", back_populates="id")


class CookieOrm(Base):
    __tablename__ = "cookie"

    uid = Column(Integer, primary_key=True)
    cookie = Column(Text)
    times = Column(Integer)

    id = relationship("ID", back_populates="cookie")


class ID(BaseModel):
    qq: int
    uid: Optional[int] = None
    mihoyo_bbs: Optional[int] = None

    class Config:
        orm_mode = True


class Cookie(BaseModel):
    uid: int
    cookie: Optional[str] = None
    times: Optional[int] = None

    class Config:
        orm_mode = True
