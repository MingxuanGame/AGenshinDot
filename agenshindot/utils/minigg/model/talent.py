from typing import Dict, List, Optional

from pydantic import BaseModel

from . import BaseInfo, CostList


class Attributes(BaseModel):
    labels: List[str]
    parameters: Dict[str, List[float]]


class Combat(BaseModel):
    name: str
    info: str
    description: Optional[str] = None
    attributes: Attributes


class Passive(BaseModel):
    name: str
    info: str


class TalentImage(BaseModel):
    combat1: str
    combat2: str
    combat3: str
    passive1: str
    passive2: str
    passive3: str


class Talent(BaseInfo):
    combat1: Combat
    combat2: Combat
    combat3: Combat
    passive1: Passive
    passive2: Passive
    passive3: Passive
    images: TalentImage
    version: str


class TalentCosts(BaseModel):
    lvl2: CostList
    lvl3: CostList
    lvl4: CostList
    lvl5: CostList
    lvl6: CostList
    lvl7: CostList
    lvl8: CostList
    lvl9: CostList
    lvl10: CostList
