from typing import List
from asyncio import gather
from functools import partial

from . import MiniGGClient, _request
from .model import Costs, RequestModel
from .model.weapon import Stats, Weapon

request = partial(_request, path="weapon")


class WeaponClient(MiniGGClient):
    async def get_info(self, name: str) -> Weapon | List[Weapon]:
        data = await request(
            params=RequestModel(
                queryLanguages=self.query_lang.value,
                resultLanguage=self.result_lang.value,
                query=name,
            )
        )
        if isinstance(data, list):
            # 多返回情况
            return list(await gather(*{self.get_info(i) for i in data}))
        else:
            return Weapon.parse_obj(data)

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
