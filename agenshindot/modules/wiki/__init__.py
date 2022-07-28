from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    ParamMatch,
    UnionMatch,
    ForceResult,
    SpacePolicy,
)

from .data import char_work, weapon_work

channel = Channel.current()
channel.name("wiki").author("MingxuanGame").description("原神 Wiki")

WORK = {"/gwep": weapon_work, "/gchr": char_work}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                "cmd" @ UnionMatch(*WORK.keys()).space(SpacePolicy.FORCE),
                "arg" @ ParamMatch(),
            )
        ],
    )
)
async def handler(
    app: Ariadne, group: Group, cmd: ForceResult, arg: ForceResult
):
    if arg.matched:
        await app.send_message(group, "请稍等，正在获取数据")
        await WORK[cmd.result.display](app, group, arg.result.display)
