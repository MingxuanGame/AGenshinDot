from __future__ import annotations

from functools import partial
from asyncio import gather, create_task
from typing import Set, List, Tuple, Optional

from loguru import logger
from graia.saya import Channel
from graia.scheduler import timers
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend
from graia.ariadne.message.element import Source
from graia.scheduler.saya import SchedulerSchema
from graia.ariadne.message.parser.base import MatchContent
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage

from agenshindot.config import load_config
from agenshindot.utils import cookie_str_to_mapping
from agenshindot.database.engine import Database, get_db
from agenshindot.utils.mihoyo_bbs.base import get_account
from agenshindot.utils.mihoyo_bbs.request import StatusError
from agenshindot.database.model.id_and_cookie import (
    ID,
    IDOrm,
    Cookie,
    CookieOrm,
    PublicCookie,
    PublicCookieOrm,
)

channel = Channel.current()
channel.name("bind").author("MingxuanGame").description(
    "原神 校验 Cookie 是否可用"
)
VALID_TEMPLATE = "UID {uid} 的 Cookie 可用"
INVALID_TEMPLATE = "UID {uid} 的 Cookie 已失效"
UNKNOWN_TEMPLATE = "UID {uid} 的 Cookie 状态未知 - {e}"
SMALL_MESSAGE = """=== Cookie 校验已完成 ===
有效 Cookie: {}
无效 Cookie: {}
未知状态 Cookie: {}
总计 {} 个 Cookie"""
PUBLIC_COOKIE_TEMPLATE = """公共 Cookie:
有效: {}，无效: {}，未知状态: {}
总计 {} 个公共 Cookie"""
BINDER_MESSAGE = """[AGenshinDot] 你的 Cookie 已经失效，请重新绑定
绑定命令: /gbind cookie
获取 Cookie: https://github.com/KimigaiiWuyi/GenshinUID/issues/255"""
CONFIG = load_config()
SEND_MESSAGE = CONFIG.send_message_to_binder
ADMINS = CONFIG.admins


@channel.use(SchedulerSchema(timers.crontabify("30 2 * * * 0")))
async def timer(app: Ariadne):
    logger.info("schedule")
    db = get_db()
    if not db:
        return
    await check_cookie(app, db, ADMINS)


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
        await app.send_message(
            event, "E: 数据库未开启，请联系机器人管理员", quote=source
        )
        return
    await check_cookie(app, db, event)


async def check_cookie(
    app: Ariadne, db: Database, target: GroupMessage | FriendMessage | Set[int]
):  # sourcery skip: low-code-quality
    if not isinstance(target, set):
        await app.send_message(target, "请稍等，正在校验")

    cookies = [
        Cookie.from_orm(cookie)
        for cookie in await db.fetch(CookieOrm)
        if cookie.cookie
    ]
    public_cookies = [
        PublicCookie.from_orm(cookie)
        for cookie in await db.fetch(PublicCookieOrm)
    ]

    valid_cookie: List[Cookie | PublicCookie] = []
    invalid_cookie: List[Cookie | PublicCookie] = []
    unknown_cookie: List[Tuple[Cookie | PublicCookie, Exception]] = []

    def get_account_task(cookie):
        return create_task(get_account(cookie_str_to_mapping(cookie.cookie)))

    results = await gather(
        *[
            get_account_task(cookie)
            for cookie in cookies + public_cookies
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
            if isinstance(i, Cookie)
        ]
        + [
            create_task(db.delete(PublicCookieOrm, PublicCookieOrm.id == i.id))
            for i in invalid_cookie
            if isinstance(i, PublicCookie)
        ]
    )

    friends = [friend.id for friend in await app.get_friend_list()]
    if SEND_MESSAGE:
        for i in invalid_cookie:
            if isinstance(i, Cookie):
                id_ = list(await db.fetch(IDOrm, IDOrm.uid == i.uid))
                if id_:
                    id_ = ID.from_orm(id_[0])
                    if id_.qq in friends:
                        await app.send_friend_message(id_.qq, BINDER_MESSAGE)

    if len(cookies) + len(public_cookies) > 40:
        send_msg = partial(
            app.send_message,
            message=SMALL_MESSAGE.format(
                len(valid_cookie),
                len(invalid_cookie),
                len(unknown_cookie),
                len(valid_cookie) + len(invalid_cookie) + len(unknown_cookie),
            ),
        )
    else:
        msg = ""
        valid_public_cookie = invalid_public_cookie = unknown_public_cookie = 0
        for i in valid_cookie:
            if isinstance(i, Cookie):
                msg += VALID_TEMPLATE.format(uid=i.uid) + "\n"
            else:
                valid_public_cookie += 1
        for i in invalid_cookie:
            if isinstance(i, Cookie):
                msg += INVALID_TEMPLATE.format(uid=i.uid) + "\n"
            else:
                invalid_public_cookie += 1
        for i, e in unknown_cookie:
            if isinstance(i, Cookie):
                msg += UNKNOWN_TEMPLATE.format(uid=i.uid, e=e) + "\n"
            else:
                unknown_public_cookie += 1
        send_msg = partial(
            app.send_message,
            message="Cookie 校验已完成\n"
            + msg
            + PUBLIC_COOKIE_TEMPLATE.format(
                valid_public_cookie,
                invalid_public_cookie,
                unknown_public_cookie,
                len(public_cookies),
            ),
        )
    if isinstance(target, set):
        admins: List[Optional[Friend]] = await gather(
            *[create_task(app.get_friend(id_)) for id_ in target]
        )
        await gather(
            *[
                create_task(send_msg(target=friend))
                for friend in admins
                if friend
            ]
        )
    else:
        await send_msg(target=target)
