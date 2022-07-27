from typing import List, Optional

from pydantic import Field, HttpUrl, BaseModel

from . import BaseInfo, FandomUrl


class Image(BaseModel):
    name_icon: str = Field(..., alias="nameicon")


# === Food === #


class Effect(BaseModel):
    effect: str
    description: str


class Ingredient(BaseModel):
    name: str
    count: int


class Food(BaseInfo):
    name: str
    rarity: str
    food_type: str = Field(..., alias="foodtype")
    food_filter: str = Field(..., alias="foodfilter")
    food_category: str = Field(..., alias="foodcategory")
    effect: str
    description: str
    suspicious: Optional[Effect] = None
    normal: Optional[Effect] = None
    delicious: Optional[Effect] = None
    ingredients: List[Ingredient]
    images: Image
    url: Optional[FandomUrl]
    version: str


# === Enemies === #


class Investigation(BaseModel):
    name: str
    category: str
    description: str


class EnemiesRewardItem(BaseModel):
    name: str
    count: Optional[float] = None


class Enemies(BaseInfo):
    special_name: str = Field(..., alias="specialname")
    enemy_type: str = Field(..., alias="enemytype")
    category: str
    description: str
    investigation: Investigation
    reward_item: List[EnemiesRewardItem] = Field(..., alias="rewardpreview")
    images: Image
    version: str


# === Domain === #


class DomainRewardItem(BaseModel):
    name: str
    count: Optional[int] = None
    rarity: Optional[str] = None


class DomainImage(BaseModel):
    name_pic: str = Field(..., alias="namepic")


class Domain(BaseInfo):
    region: str
    domain_entrance: str = Field(..., alias="domainentrance")
    domain_type: str = Field(..., alias="domaintype")
    description: str
    recommended_level: int = Field(..., alias="recommendedlevel")
    recommended_elements: List[str] = Field(..., alias="recommendedelements")
    unlock_rank: int = Field(..., alias="unlockrank")
    reward_item: List[DomainRewardItem] = Field(..., alias="rewardpreview")
    disorder: List[str]
    monster_list: List[str] = Field(..., alias="monsterlist")
    images: DomainImage
    version: str


# === Artifact === #


class Artifact(BaseModel):
    name: str
    relic_type: str = Field(..., alias="relictype")
    description: str


class ArtifactImage(BaseModel):
    flower: HttpUrl
    plume: HttpUrl
    sands: HttpUrl
    goblet: HttpUrl
    circlet: HttpUrl
    name_flower: str = Field(..., alias="nameflower")
    name_plume: str = Field(..., alias="nameplume")
    name_sands: str = Field(..., alias="namesands")
    name_goblet: str = Field(..., alias="namegoblet")
    name_circlet: str = Field(..., alias="namecirclet")


class ArtifactSet(BaseInfo):
    rarity: List[str]
    pc2: str = Field(..., alias="2pc")
    pc4: str = Field(..., alias="4pc")
    flower: Artifact
    plume: Artifact
    sands: Artifact
    goblet: Artifact
    circlet: Artifact
    images: ArtifactImage
    url: FandomUrl
    version: str


# === Material === #


class MaterialImage(Image):
    redirect: HttpUrl
    fandom: HttpUrl


class Material(BaseInfo):
    description: str
    sort_order: int = Field(..., alias="sortorder")
    rarity: str
    category: str
    material_type: str = Field(..., alias="materialtype")
    source: List[str]
    images: MaterialImage
    url: FandomUrl
    version: str
