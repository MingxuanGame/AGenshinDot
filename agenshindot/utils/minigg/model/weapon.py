from typing import List, Optional

from pydantic import Field, HttpUrl, BaseModel

from . import BaseInfo, FandomUrl

R = List[str]


class Image(BaseModel):
    image: Optional[HttpUrl]
    name_icon: str = Field(..., alias="nameicon")
    name_gacha: str = Field(..., alias="namegacha")
    icon: HttpUrl
    name_awaken_icon: str = Field(..., alias="nameawakenicon")
    awaken_icon: HttpUrl = Field(..., alias="awakenicon")


class Weapon(BaseInfo):
    description: str
    weapon_type: str = Field(..., alias="weapontype")
    rarity: str
    base_atk: int = Field(..., alias="baseatk")
    sub_stat: str = Field(..., alias="substat")
    sub_value: str = Field(..., alias="subvalue")
    effect_name: str = Field(..., alias="effectname")
    effect: str
    r1: R
    r2: R
    r3: R
    r4: R
    r5: R
    weapon_material_type: str = Field(..., alias="weaponmaterialtype")
    images: Image
    url: Optional[FandomUrl]
    version: str


class Stats(BaseModel):
    level: int
    ascension: int
    attack: float
    specialized: float
