from typing import List
from asyncio import gather
from functools import partial

from .model import RequestModel
from . import MiniGGClient, _request
from .model.other import Food, Domain, Enemies, Material, ArtifactSet

food_request = partial(_request, path="food")
enemies_request = partial(_request, path="enemies")
domain_request = partial(_request, path="domain")
artifact_request = partial(_request, path="artifact")
material_request = partial(_request, path="material")


class FoodClient(MiniGGClient):
    async def get_info(self, name: str) -> Food | List[Food]:
        data = await food_request(
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
            return Food.parse_obj(data)


class EnemiesClient(MiniGGClient):
    async def get_info(self, name: str) -> Enemies:
        return Enemies.parse_obj(
            await enemies_request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                )
            )
        )


class DomainClient(MiniGGClient):
    async def get_info(self, name: str) -> Domain | List[Domain]:
        data = await domain_request(
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
            return Domain.parse_obj(data)


class ArtifactClient(MiniGGClient):
    async def get_info(self, name: str) -> ArtifactSet:
        return ArtifactSet.parse_obj(
            await artifact_request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                )
            )
        )


class MaterialClient(MiniGGClient):
    async def get_info(self, name: str) -> Material:
        return Material.parse_obj(
            await material_request(
                params=RequestModel(
                    queryLanguages=self.query_lang.value,
                    resultLanguage=self.result_lang.value,
                    query=name,
                )
            )
        )
