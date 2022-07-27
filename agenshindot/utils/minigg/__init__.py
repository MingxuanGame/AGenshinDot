from __future__ import annotations

import abc
from enum import Enum
from typing import Any, Dict, List

from yarl import URL
from aiohttp import ClientSession

from .exception import APINotFound
from .model import BaseInfo, RequestModel
from .exception import NotFoundError as NotFoundError


class Lang(Enum):
    CHS = "ChineseSimplified"
    CHT = "ChineseTraditional"
    JP = "Japanese"
    EN = "English"
    FR = "French"
    DE = "German"
    ID = "ID"
    KR = "Korean"
    PT = "Portuguese"
    RU = "Russian"
    ES = "Spanish"
    TH = "Thai"
    VI = "Vietnamese"


BASE_API = URL("https://info.minigg.cn")
PATHS: Dict[str, URL] = {
    "character": BASE_API / "characters",
    "weapon": BASE_API / "weapons",
    "constellation": BASE_API / "constellations",
    "talent": BASE_API / "talents",
    "food": BASE_API / "foods",
    "enemies": BASE_API / "enemies",
    "domain": BASE_API / "domains",
    "artifact": BASE_API / "artifacts",
    "material": BASE_API / "materials",
}


class MiniGGClient(abc.ABC):
    def __init__(
        self,
        query_lang: Lang = Lang.CHS,
        result_lang: Lang = Lang.CHS,
    ):
        self.query_lang = query_lang
        self.result_lang = result_lang

    @abc.abstractmethod
    async def get_info(self, name: str) -> BaseInfo | List[BaseInfo]:
        raise NotImplementedError


async def _request(
    path: str, params: RequestModel
) -> Dict[str, Any] | List[str]:
    if api := PATHS.get(path):
        async with ClientSession() as session:
            resp = await session.get(
                api, params=params.dict(by_alias=True, exclude_none=True)
            )
            if resp.status == 404:
                raise NotFoundError(path, params.query)
            resp.raise_for_status()
            return await resp.json()
    raise APINotFound(path)


__all__ = ["model", "character", "exception", "other", "weapon"]
