from __future__ import annotations

from typing import List

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Source
from graia.ariadne.message.commander.saya import CommandSchema

from ...config import load_config
from ...database.engine import get_db
from ...utils.mihoyo_bbs.base import get_server
from ...database.model.id_and_cookie import ID, IDOrm
from ...modules.mihoyo_bbs.data import draw, get_cookie

channel = Channel.current()
channel.name("mihoyo_bbs").author("MingxuanGame").description("原神米游社查询")
ADMINS = load_config().admins


@channel.use(CommandSchema("/guid {uid: int = 0}"))
@channel.use(CommandSchema("/guid {...uid: At}"))
async def handler(
    app: Ariadne,
    source: Source,
    group: Group,
    member: Member,
    uid: int | List[At],
):
    if isinstance(uid, list):
        if not uid:
            return
        if member.id not in ADMINS:
            await app.send_message(group, "你不是机器人管理员，无权操作", quote=source)
            return
        db = get_db()
        user = uid[0]
        if not db:
            await app.send_message(group, "E: 数据库未开启，请联系机器人管理员", quote=source)
            return
        uid = await db.select(IDOrm, user.target)
        if not uid:
            await app.send_message(
                group, MessageChain("未找到", user, "的 UID 信息"), quote=source
            )

            return
        id_ = ID.from_orm(uid).uid
        if not id_:
            await app.send_message(
                group, MessageChain("未找到", user, "的 UID 信息"), quote=source
            )

            return
        uid = id_
    db = get_db()
    if not db:
        await app.send_message(group, "E: 数据库未开启，请联系机器人管理员", quote=source)
        return
    if uid == 0:
        uid_db = await db.select(IDOrm, member.id)
        if (
            not uid_db
            or not (model := ID.from_orm(uid_db))
            or model.uid is None
        ):
            await app.send_message(
                group,
                MessageChain("未找到", At(member), "的 UID 信息"),
                quote=source,
            )

            return
        uid = model.uid
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
        bio.seek(0)
        await app.send_message(group, Image(data_bytes=bio))
