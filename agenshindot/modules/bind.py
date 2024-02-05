from __future__ import annotations

from typing import Tuple

from loguru import logger
from graia.saya import Channel
from pydantic import ValidationError
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Source
from graia.ariadne.model import Group, Friend, Member
from graia.ariadne.util.interrupt import FunctionWaiter
from aiohttp import ClientResponseError, ClientConnectorError
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    UnionMatch,
    ForceResult,
    SpacePolicy,
    WildcardMatch,
)

from agenshindot.config import load_config
from agenshindot.utils import cookie_str_to_mapping
from agenshindot.database.engine import Database, get_db
from agenshindot.utils.mihoyo_bbs.request import StatusError
from agenshindot.utils.mihoyo_bbs.base import get_server, get_account
from agenshindot.database.model.id_and_cookie import ID, IDOrm, CookieOrm
from agenshindot.utils.mihoyo_bbs.model.base import (
    CNAccount,
    OSAccount,
    CNAccounts,
    OSAccounts,
)

channel = Channel.current()
channel.name("bind").author("MingxuanGame").description(
    "原神 绑定 UID/米游社通行证/cookie"
)
IS_DISABLE = not load_config().enable_bind_cookie
WARNING = """警告：
Cookie 为敏感信息，其效力相当于账号密码
Cookie 会被明文存储在数据库中，且日志中也会储存 Cookie 明文
这意味着机器人管理员等人可以通过查阅数据库等方式获取到你的 Cookie 来登录你的米游社账号"
如果你感觉到 Cookie 被盗，请立即修改密码
AGenshinDot 项目及作者不承担因 Cookie 泄露所造成的一切后果
如果要继续绑定 Cookie，请继续输入 Cookie，输入 no 或者不输入（如果命令中含有 Cookie 则会继续）取消绑定
"""

twilight = Twilight(
    FullMatch("/gbind").space(SpacePolicy.FORCE),
    "cmd" @ UnionMatch("uid", "mys", "cookie"),
    FullMatch(" ", optional=True),
    "arg" @ WildcardMatch(optional=True),
)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[twilight],
    )
)
async def group_handler(
    cmd: ForceResult,
    arg: ForceResult,
    app: Ariadne,
    group: Group,
    member: Member,
    source: Source,
):
    if cmd.matched:
        cmd_display = cmd.result.display
        try:
            if cmd_display == "cookie":
                if group.account_perm > member.permission:
                    await app.recall_message(source)
                    msg_start = "群聊中不允许绑定 Cookie，已撤回"
                else:
                    msg_start = "群聊中不允许绑定 Cookie"
                await app.send_group_message(
                    group,
                    MessageChain(
                        At(member),
                        (
                            msg_start
                            + f"{'（本机器人未开启 Cookie 绑定）' if IS_DISABLE else ''}"
                            "\n如果觉得有盗号风险请立即退出登录来刷新 Cookie"
                        ),
                    ),
                    quote=source,
                )
                return
            else:
                if arg.matched:
                    await bind_uid_or_mihoyo_id_chat(
                        app, source, member.id, group, cmd_display, arg
                    )
        except Exception as e:
            logger.exception("Error at draw(group_handler)")
            return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[twilight],
    )
)
async def friend_handler(
    cmd: ForceResult,
    arg: ForceResult,
    app: Ariadne,
    friend: Friend,
    source: Source,
):
    if not cmd.matched:
        return
    cmd_display = cmd.result.display
    try:
        if cmd_display in ["uid", "mys"]:
            if arg.matched:
                await bind_uid_or_mihoyo_id_chat(
                    app, source, friend.id, friend, cmd_display, arg
                )
        else:
            if IS_DISABLE:
                await app.send_friend_message(
                    friend, "本机器人未开启 Cookie 绑定", quote=source
                )
                return
            db = get_db()
            if not db:
                await app.send_friend_message(
                    friend, "E: 数据库未开启，请联系机器人管理员", quote=source
                )
                return
            await app.send_friend_message(
                friend,
                WARNING,
            )

            async def cookie_accept(
                msg: MessageChain, source: Source
            ) -> Tuple[str, Source]:
                return msg.display, source

            cookie_and_source = await FunctionWaiter(
                cookie_accept, [FriendMessage]
            ).wait(timeout=30)
            if cookie_and_source is None:
                if arg.matched and (arg_str := arg.result.display):
                    cookie_str = arg_str
                    source = source
                else:
                    return
            else:
                cookie_str, source = cookie_and_source
                if cookie_str == "no":
                    return
            cookie = cookie_str_to_mapping(cookie_str)
            try:
                account = await get_account(cookie)
                if isinstance(account, CNAccounts):
                    is_os = False
                    accounts = list(
                        filter(lambda x: x.is_genshin(), account.list)
                    )
                else:
                    is_os = True
                    accounts = account.list
                if len(accounts) == 1:
                    index = 0
                else:
                    await app.send_friend_message(
                        friend,
                        "存在多个账号，请输入序号来选择绑定的 UID（默认为0）\n"
                        + "\n".join(
                            [
                                f"{i}: {account__.game_uid} - "
                                f"{account__.region_name} - "
                                f"Lv. {account__.level}"
                                for i, account__ in enumerate(accounts)
                            ]
                        ),
                        quote=source,
                    )

                    async def waiter(msg: MessageChain) -> Tuple[int, bool]:
                        msg_str = msg.display
                        if not msg_str.isdigit():
                            return 0, False
                        msg_int = int(msg_str)
                        if msg_int < 0 or msg_int > len(accounts) - 1:
                            return 0, False
                        return msg_int, True

                    result = await FunctionWaiter(
                        waiter, [FriendMessage]
                    ).wait(timeout=60, default=(0, False))
                    if not result[1]:
                        await app.send_friend_message(
                            friend,
                            "警告：选择超时或输入无效，已选择默认项",
                            quote=source,
                        )
                    index = result[0]
                await bind_cookie(
                    source,
                    friend,
                    app,
                    db,
                    is_os,
                    cookie_str,
                    account,
                    accounts[index],
                )
            except ClientConnectorError as e:
                await app.send_friend_message(
                    friend,
                    f"E: 无法访问 米游社 API - {e.strerror}",
                    quote=source,
                )
            except ClientResponseError as e:
                await app.send_friend_message(
                    friend,
                    f"E: 米游社 API HTTP 状态码异常 - {e.code} {e.message}",
                    quote=source,
                )
            except StatusError as e:
                await app.send_friend_message(
                    friend,
                    (
                        f"E: 米游社状态异常: {e.status}\n"
                        "请检查 Cookie 或重新抓取\n获取 Cookie: "
                        "https://github.com/KimigaiiWuyi/GenshinUID/issues/255"
                    ),
                    quote=source,
                )
            except ValidationError as e:
                await app.send_friend_message(
                    friend, f"E: 解析数据出现异常:\n{e}", quote=source
                )
            except ValueError:
                await app.send_friend_message(
                    friend,
                    "E: Cookie 不合法：未找到 account_id 或 ltuid，请检查输入",
                    quote=source,
                )
            return
    except Exception as e:
        logger.exception("Error at draw(friend_handler)")
        return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"


async def bind_cookie(
    source: Source,
    friend: Friend,
    app: Ariadne,
    db: Database,
    is_os: bool,
    cookie_str: str,
    account: CNAccounts | OSAccounts,
    account_: CNAccount | OSAccount,
):
    msg = (
        await bind_uid_or_mihoyo_id(friend.id, True, int(account_.game_uid))
        + "\n"
        + await bind_uid_or_mihoyo_id(friend.id, False, account.mihoyo_id)
    )
    uid = int(account_.game_uid)
    is_insert = await db.insert_or_update(
        CookieOrm,
        uid,
        uid=uid,
        cookie=cookie_str,
        times=0,
    )
    await app.send_friend_message(
        friend,
        (
            "Cookie 绑定成功！\n"
            if is_insert
            else "Cookie 曾绑定过，本次绑定已覆盖\n"
        )
        + msg
        + ("（Cookie 为国际服 Cookie）" if is_os else ""),
        quote=source,
    )


async def bind_uid_or_mihoyo_id_chat(
    app: Ariadne,
    source: Source,
    qq: int,
    target: Group | Friend,
    cmd_display: str,
    arg: ForceResult,
):
    if not arg.result.display.isdigit():
        await app.send_message(
            target, "E: UID/米游社通行证需为数字，请检查输入", quote=source
        )
        return
    id_ = int(arg.result.display)
    await app.send_message(
        target,
        await bind_uid_or_mihoyo_id(qq, cmd_display == "uid", id_),
        quote=source,
    )


async def bind_uid_or_mihoyo_id(qq: int, is_uid: bool, value: int) -> str:
    db = get_db()
    if not db:
        return "E: 数据库未开启，请联系机器人管理员"
    latest_data = await db.select(IDOrm, qq)
    name, key = ("UID", "uid") if is_uid else ("米游社通行证", "mihoyo_id")
    if is_uid:
        try:
            if not get_server(value):
                raise ValueError
        except ValueError:
            return "E: UID 不合法，请检查输入"

    async def update(
        db: Database,
        key: str,
        value: int,
        is_uid: bool,
        model: ID,
        is_overwrite: bool,
    ):
        await db.update(IDOrm, IDOrm.qq == qq, **{key: value})
        if is_uid and list(
            await db.fetch(CookieOrm, CookieOrm.uid == model.uid)
        ):
            await db.update(CookieOrm, CookieOrm.uid == model.uid, uid=value)
        if is_overwrite:
            return (
                f"{name} 曾绑定过，本次绑定已覆盖\n上一次绑定的 "
                f"{name} 为 {getattr(model, key, None)}"
            )
        return f"{name} 绑定成功！"

    if latest_data is None:
        await db.insert(IDOrm, **{"qq": qq, key: value})
        return f"{name} 绑定成功！"
    else:
        model = ID.from_orm(latest_data)
        return await update(
            db, key, value, is_uid, model, getattr(model, key, None) is None
        )
