from typing import List

from pydantic import Field, BaseModel

# === Base Info === #


class Role(BaseModel):
    avatar_url: str = Field(..., alias="AvatarUrl")
    nickname: str
    region: str
    level: int


class Avatar(BaseModel):
    id: int
    image: str
    name: str
    element: str
    fetter: int
    level: int
    rarity: int
    actived_constellation_num: int
    card_image: str
    is_chosen: bool


class Stats(BaseModel):
    active_day_number: int
    achievement_number: int
    anemoculus_number: int
    geoculus_number: int
    avatar_number: int
    way_point_number: int
    domain_number: int
    spiral_abyss: str
    precious_chest_number: int
    luxurious_chest_number: int
    exquisite_chest_number: int
    common_chest_number: int
    electroculus_number: int
    magic_chest_number: int


class Offering(BaseModel):
    name: str
    level: int
    icon: str


class World(BaseModel):
    level: int
    exploration_percentage: int
    icon: str
    name: str
    type: str
    offerings: List[Offering]
    id: int
    parent_id: int
    map_url: str
    strategy_url: str
    background_image: str
    inner_icon: str
    cover: str


class Home(BaseModel):
    level: int
    visit_num: int
    comfort_num: int
    item_num: int
    name: str
    icon: str
    comfort_level_name: str
    comfort_level_icon: str


class Info(BaseModel):
    role: Role
    avatars: List[Avatar]
    stats: Stats
    # city_explorations: List[Any]  # unused?
    world_explorations: List[World]
    homes: List[Home]


# === Account Info === #


class CNAccount(BaseModel):
    game_biz: str
    region: str
    game_uid: str
    nickname: str
    level: int
    is_chosen: bool
    region_name: str
    is_official: bool

    def is_genshin(self) -> bool:
        return self.game_biz == "hk4e_cn"


class CNAccounts(BaseModel):
    mihoyo_id: int
    list: List[CNAccount]


class OSAccount(BaseModel):
    has_role: bool
    game_id: int
    game_uid: str = Field(..., alias="game_role_id")  # 与国服字段同步
    nickname: str
    region: str
    level: int
    background_image: str
    is_public: bool
    region_name: str
    url: str


class OSAccounts(BaseModel):
    mihoyo_id: int
    list: List[OSAccount]
