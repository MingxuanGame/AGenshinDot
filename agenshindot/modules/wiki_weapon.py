from datetime import datetime

from yarl import URL
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.element import Image, Plain, Forward, ForwardNode
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ParamMatch,
    ForceResult,
    SpacePolicy,
)

from ..utils.minigg.model.weapon import Weapon
from ..utils.minigg.weapon import WeaponClient

channel = Channel.current()
channel.name("wiki-weapon").author("MingxuanGame").description("Wiki - 获取武器信息")

BWIKI = URL("https://wiki.biligame.com/ys")
WEAPON_TEMPLATE = """=== 基础信息 ===
【名称】{name}
【简介】{description}
【类型】{weapon_type}
【稀有度】{rarity}
=== 属性 ===
【基础攻击力】{base_atk}\n"""
EFFECT_TEMPLATE = "=== 武器效果 ===\n【名称】{name}效果：\n"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                FullMatch("/gwep").space(SpacePolicy.FORCE),
                "weapon" @ ParamMatch(),
            )
        ],
    )
)
async def weapon_func(app: Ariadne, group: Group, weapon: ForceResult):
    if weapon.matched:
        client = WeaponClient()
        name = str(weapon.result)
        await app.send_message(group, "请稍等，正在获取数据")
        data = await client.get_info(name)
        if not isinstance(data, list):
            await app.send_message(group, make_message(data))
        else:
            await app.send_message(
                group,
                Forward(
                    [
                        ForwardNode(
                            target=app.account,
                            time=datetime.now(),
                            message=make_message(i),
                            name="AGenshinDot",
                        )
                        for i in data
                    ]
                ),
            )


def make_message(weapon: Weapon) -> MessageChain:
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
