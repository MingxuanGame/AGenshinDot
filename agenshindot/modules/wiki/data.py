from __future__ import annotations

from typing import Dict, List, Coroutine

from yarl import URL
from loguru import logger
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from aiohttp import ClientResponseError, ClientConnectorError

from ...utils import send_msg_auto_forward
from ...utils.minigg.model.weapon import Weapon
from ...utils.minigg.weapon import WeaponClient
from ...utils.minigg.exception import NotFoundError
from ...utils.minigg.character import CharacterClient
from ...utils.minigg.model.character import Character

BWIKI = URL("https://wiki.biligame.com/ys")

WEAPON_TEMPLATE = """=== 基础信息 ===
【名称】{name}
【简介】{description}
【类型】{weapon_type}
【稀有度】{rarity}
=== 属性 ===
【基础攻击力】{base_atk}\n"""
EFFECT_TEMPLATE = "=== 武器效果 ===\n【名称】{name}效果：\n"

CHAR_TEMPLATE = """=== {name} - {title} ===
【简介】{description}
【元素】{element}
【稀有度】{rarity}
【武器类型】{weapon_type}
【所属】{region}
【生日】{birthday}
【命之座】{constellation}"""

TYPE: Dict[str, str] = {"character": "角色", "weapon": "武器"}


async def get_info_catch_exception(get_info: Coroutine):
    try:
        return await get_info
    except ClientConnectorError as e:
        return f"E: 无法访问 MiniGG API - {e.strerror}"
    except ClientResponseError as e:
        return f"E: MiniGG API HTTP 状态码异常 - {e.code} {e.message}"
    except NotFoundError as e:
        return f"E: 没有此{TYPE.get(e.type_)} - {e.name}"
    except Exception as e:
        logger.exception("Error at get_info_catch_exception")
        return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"


async def get_weapon_info(name: str) -> Weapon | List[Weapon] | str:
    client = WeaponClient()
    return await get_info_catch_exception(client.get_info(name))


def make_weapon_message(weapon: Weapon) -> MessageChain:
    msg = WEAPON_TEMPLATE.format(**weapon.dict())
    if weapon.sub_stat:
        msg += f"{weapon.sub_stat}+{weapon.sub_value}"
    if weapon.effect:
        msg += "\n" + EFFECT_TEMPLATE.format(name=weapon.effect_name)
        if not weapon.r1:
            msg += weapon.effect
        else:
            for i, v in enumerate(
                (weapon.r1, weapon.r2, weapon.r3, weapon.r4, weapon.r5)
            ):
                msg += f"【精炼{i + 1}阶】{weapon.effect.format(*v)}\n"
    if url := weapon.url:
        msg += f"Fandom: {url.fandom}\n"
    msg += f"BWiki: {BWIKI / weapon.name}\n"
    return MessageChain([Plain(msg), Image(url=weapon.images.image)])


async def weapon_work(app: Ariadne, group: Group, name: str):
    data = await get_weapon_info(name)
    if isinstance(data, str):
        await app.send_message(group, f"获取武器信息出现错误：\n{data}")
        return
    chain = (
        [make_weapon_message(i) for i in data]
        if isinstance(data, list)
        else make_weapon_message(data)
    )

    await send_msg_auto_forward(app, group, chain)


async def get_character_info(name: str) -> Character | List[Character] | str:
    client = CharacterClient()
    return await get_info_catch_exception(client.get_info(name))


def make_character_message(char: Character) -> MessageChain:
    chain = MessageChain(
        [
            Plain(
                CHAR_TEMPLATE.format(**char.dict())
                + f"\n【中文CV】{char.cv.chinese}"
                + f"\nBWiki: {BWIKI / char.name}"
                + (f"Fandom: {char.url.fandom}\n" if char.url else "")
            )
        ]
    )
    if card := char.images.card:
        chain.append(Image(url=card))
    return chain


async def char_work(app: Ariadne, group: Group, name: str):
    data = await get_character_info(name)
    if isinstance(data, str):
        await app.send_message(group, f"获取角色信息出现错误：\n{data}")
        return
    chain = (
        [make_character_message(i) for i in data]
        if isinstance(data, list)
        else make_character_message(data)
    )

    await send_msg_auto_forward(app, group, chain)
