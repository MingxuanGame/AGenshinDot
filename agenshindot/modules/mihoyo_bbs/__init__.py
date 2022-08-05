from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image, Source
from graia.ariadne.message.commander.saya import CommandSchema

from .data import draw, get_cookie
from ...utils.mihoyo_bbs.base import get_server

channel = Channel.current()
channel.name("mihoyo_bbs").author("MingxuanGame").description("原神米游社查询")


@channel.use(CommandSchema("/uid {uid}"))
async def handler(
    app: Ariadne,
    # event: MessageEvent,
    source: Source,
    group: Group,
    member: Member,
    uid: int,
):
    try:
        get_server(uid)
    except ValueError:
        await app.send_message(group, "UID 不合法，请检查 UID", quote=source)
        return
    cookie = await get_cookie(uid)
    if isinstance(cookie, str):
        await app.send_message(group, cookie, quote=source)
        return
    await app.send_message(group, "请稍等，正在获取数据", quote=source)
    bio = await draw(uid, cookie, await member.get_avatar(), member.name)
    if isinstance(bio, str):
        await app.send_message(group, bio, quote=source)
    else:
        bio.seek(0)  # 别问，问就是 img.save(bio) 写到文件末尾了
        await app.send_message(group, Image(data_bytes=bio))
