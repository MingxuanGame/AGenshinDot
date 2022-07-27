from typing import List, Optional

from pydantic import Field, HttpUrl, BaseModel


class RequestModel(BaseModel):
    queryLanguages: str = Field("CHS")
    resultLanguage: str = Field("CHS")
    query: str
    costs: Optional[int] = None
    stats: Optional[int] = None
    c: Optional[int] = None


class BaseInfo(BaseModel):
    name: str


class FandomUrl(BaseModel):
    fandom: HttpUrl


class Cost(BaseModel):
    name: str
    count: int


CostList = List[Cost]


class Costs(BaseModel):
    ascend1: CostList
    ascend2: CostList
    ascend3: CostList
    ascend4: CostList
    ascend5: CostList
    ascend6: CostList


__all__ = ["character", "talent", "other", "weapon"]
