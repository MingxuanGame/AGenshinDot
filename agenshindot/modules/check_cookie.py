from __future__ import annotations

from typing import List, Tuple
from asyncio import gather, create_task

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Source
from graia.ariadne.message.parser.base import MatchContent
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage

from ..config import load_config
from ..database.engine import get_db
from ..utils import cookie_str_to_mapping
from ..utils.mihoyo_bbs.base import get_account
from ..utils.mihoyo_bbs.request import StatusError
from ..database.model.id_and_cookie import ID, IDOrm, Cookie, CookieOrm

channel = Channel.current()
channel.name("bind").author("MingxuanGame").description("原神 校验 Cookie 是否可用")
VALID_TEMPLATE = "UID {uid} 的 Cookie 可用"
INVALID_TEMPLATE = "UID {uid} 的 Cookie 已失效"
UNKNOWN_TEMPLATE = "UID {uid} 的 Cookie 状态未知 - {e}"
SMALL_MESSAGE = """Cookie 校验已完成
有效 Cookie: {}
无效 Cookie: {}
未知状态 Cookie: {}
总计 {} 个 Cookie"""
BINDER_MESSAGE = """[AGenshinDot] 你的 Cookie 已经失效，请重新绑定
绑定命令: /gbind cookie
获取 Cookie: https://github.com/KimigaiiWuyi/GenshinUID/issues/255"""
SEND_MESSAGE = load_config().send_message_to_binder


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        decorators=[MatchContent(content="/gcheck")],
    )
)
async def handler(
    app: Ariadne, event: GroupMessage | FriendMessage, source: Source
):
    db = get_db()
    if not db:
        await app.send_message(event, "E: 数据库未开启，请联系机器人管理员", quote=source)
        return
    await app.send_message(event, "请稍等，正在校验", quote=source)
    cookies = [
        Cookie.from_orm(cookie)
        for cookie in await db.fetch(CookieOrm)
        if cookie.cookie
    ]

    valid_cookie: List[Cookie] = []
    invalid_cookie: List[Cookie] = []
    unknown_cookie: List[Tuple[Cookie, Exception]] = []
    results = await gather(
        *[
            create_task(get_account(cookie_str_to_mapping(cookie.cookie)))
            for cookie in cookies
            if cookie.cookie
        ],
        return_exceptions=True,
    )
    for i, result in enumerate(results):
        if isinstance(result, StatusError):
            invalid_cookie.append(cookies[i])
        elif isinstance(result, Exception):
            unknown_cookie.append((cookies[i], result))
        else:
            valid_cookie.append(cookies[i])

    await gather(
        *[
            create_task(db.delete(CookieOrm, CookieOrm.uid == i.uid))
            for i in invalid_cookie
        ]
    )

    friends = [friend.id for friend in await app.get_friend_list()]
    if SEND_MESSAGE:
        for i in invalid_cookie:
            id_ = list(await db.fetch(IDOrm, IDOrm.uid == i.uid))
            if id_:
                id_ = ID.from_orm(id_[0])
                if id_.qq in friends:
                    await app.send_friend_message(id_.qq, BINDER_MESSAGE)

    if len(cookies) > 20:
        await app.send_message(
            event,
            SMALL_MESSAGE.format(
                len(valid_cookie),
                len(invalid_cookie),
                len(unknown_cookie),
                len(valid_cookie) + len(invalid_cookie) + len(unknown_cookie),
            ),
            quote=source,
        )
        return
    msg = "".join(
        VALID_TEMPLATE.format(uid=i.uid) + "\n" for i in valid_cookie
    )
    for i in invalid_cookie:
        msg += INVALID_TEMPLATE.format(uid=i.uid) + "\n"
    for i, e in unknown_cookie:
        msg += UNKNOWN_TEMPLATE.format(uid=i.uid, e=e) + "\n"
    await app.send_message(event, "Cookie 校验已完成\n" + msg, quote=source)
