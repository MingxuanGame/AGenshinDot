from typing import Optional

from pydantic import Field, HttpUrl, BaseModel

from . import BaseInfo, FandomUrl


class CV(BaseModel):
    english: str
    chinese: str
    japanese: str
    korean: str


class Image(BaseModel):
    card: Optional[HttpUrl] = None
    portrait: Optional[HttpUrl] = None
    icon: HttpUrl
    side_icon: HttpUrl = Field(..., alias="sideicon")
    cover1: Optional[HttpUrl] = None
    cover2: Optional[HttpUrl] = None
    hoyolab_avatar: Optional[HttpUrl] = Field(None, alias="hoyolab-avatar")
    name_icon: str = Field(..., alias="nameicon")
    name_icon_card: str = Field(..., alias="nameiconcard")
    name_gacha_splash: Optional[str] = Field(None, alias="namegachasplash")
    name_gacha_slice: Optional[str] = Field(None, alias="namegachaslice")
    name_side_icon: str = Field(..., alias="namesideicon")


class Character(BaseInfo):
    fullname: str
    title: str
    description: str
    rarity: str
    element: str
    weapon_type: str = Field(..., alias="weapontype")
    sub_stat: str = Field(..., alias="substat")
    gender: str
    body: str
    association: str
    region: str
    affiliation: str
    birthday_mmdd: str = Field(..., alias="birthdaymmdd")
    birthday: str
    constellation: str
    cv: CV
    images: Image
    url: FandomUrl
    version: str


class Stats(BaseModel):
    level: int
    ascension: int
    hp: float
    attack: float
    defense: float
    specialized: float


class Constellation(BaseInfo):
    effect: str
