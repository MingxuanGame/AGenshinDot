from typing import List
from asyncio import gather
from functools import partial

from . import MiniGGClient, _request
from .model import Costs, RequestModel
from .model.talent import Talent, TalentCosts
from .model.character import Stats, Character, Constellation

request = partial(_request, path="character")
talent_request = partial(_request, path="talent")


class CharacterClient(MiniGGClient):
    async def get_info(self, name: str) -> Character | List[Character]:
        data = await request(
            params=RequestModel(
                queryLanguages=self.query_lang.value,
                resultLanguage=self.result_lang.value,
                query=name,
            )
        )
        if isinstance(data, list):
            # 多返回情况
            # e.g. name=草 服务器返回 ["久岐忍","宵宫"]
            # 递归获取列表内所有角色信息
            return list(await gather(*{self.get_info(i) for i in data}))
        else:
            return Character.parse_obj(data)

    async def get_costs(self, name: str) -> Costs:
        return Costs.parse_obj(
            await request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                    costs=True,
                )
            )
        )

    async def get_stats(self, name: str, stats: int) -> Stats:
        if stats > 90 or stats <= 0:
            raise ValueError("stats must <= 90 and > 0")
        return Stats.parse_obj(
            await request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                    stats=stats,
                )
            )
        )

    async def get_constellation(
        self, name: str, constellation: int
    ) -> Constellation:
        if constellation > 6 or constellation <= 0:
            raise ValueError("constellation must <= 6 and > 0")
        return Constellation.parse_obj(
            await _request(
                "constellation",
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                    c=constellation,
                ),
            )
        )

    async def get_talent(self, name: str) -> Talent:
        return Talent.parse_obj(
            await talent_request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                )
            )
        )

    async def get_talent_costs(self, name: str) -> TalentCosts:
        return TalentCosts.parse_obj(
            await talent_request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                    costs=True,
                )
            )
        )
