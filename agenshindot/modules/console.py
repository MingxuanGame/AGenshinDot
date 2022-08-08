from time import time
from sqlite3 import Warning as SqliteWarning

from loguru import logger
from rich.table import Table
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from sqlalchemy.exc import DatabaseError
from graia.ariadne.console import Console
from rich.console import Console as RichConsole
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import (
    FORCE,
    Twilight,
    FullMatch,
    ForceResult,
    WildcardMatch,
)

from agenshindot.version import __version__
from agenshindot.database.engine import get_db

channel = Channel.current()

LOGO = r"""
           _____                _     _       _____        _
     /\   / ____|              | |   (_)     |  __ \      | |
    /  \ | |  __  ___ _ __  ___| |__  _ _ __ | |  | | ___ | |_
   / /\ \| | |_ |/ _ \ '_ \/ __| '_ \| | '_ \| |  | |/ _ \| __|
  / ____ \ |__| |  __/ | | \__ \ | | | | | | | |__| | (_) | |_
 /_/    \_\_____|\___|_| |_|___/_| |_|_|_| |_|_____/ \___/ \__|
"""


@channel.use(ConsoleSchema(decorators=[MatchContent("/stop")]))
async def stop(app: Ariadne, con: Console):
    con.stop()
    app.stop()


@channel.use(ConsoleSchema(decorators=[MatchContent("/license")]))
async def license():
    logger.opt(raw=True, colors=True).info(
        "AGenshinDot 遵循 <y>GNU AGPLv3</y> 许可协议开放全部源代码\n"
    )
    logger.opt(raw=True, colors=True).info(
        "你可以在 "
        "<blue>https://github.com/MingxuanGame/AGenshinDot"
        "/blob/master/LICENSE</blue>"
        " 找到本项目的许可证\n"
    )


@channel.use(ConsoleSchema(decorators=[MatchContent("/version")]))
async def ver():
    logger.opt(raw=True, colors=True).info(f"<cyan>{LOGO}</cyan>\n")
    logger.opt(raw=True, colors=True).info(
        f"<magenta>AGenshinDot</magenta>: <green>{__version__}</green>\n"
    )


@channel.use(
    ConsoleSchema(
        [Twilight(FullMatch("/execute").space(FORCE), "cmd" @ WildcardMatch())]
    )
)
async def db_execute(cmd: ForceResult):
    if not cmd.matched:
        return
    db = get_db()
    if not db:
        logger.opt(raw=True, colors=True).error("<red>E:</red> 数据库未开启\n")
        return
    try:
        start_time = time()
        result = await db.execute(cmd.result.display)
        total = round(time() - start_time, 3)
        if result.rowcount != -1:
            logger.opt(raw=True, colors=True).info(
                f"受影响的行数: <green>{result.rowcount}</green>\n"
            )
        elif result.cursor is not None:
            console = RichConsole()
            table = Table(*(str(a[0]) for a in result.cursor.description))
            for i in result:
                table.add_row(*map(str, i))
            console.print(table)
        logger.opt(raw=True, colors=True).success(
            "SQL: <green>OK</green> " f"time: <green>{total}s</green>\n"
        )
    except DatabaseError as e:
        logger.opt(raw=True, colors=True).error(
            f"<red>E:</red> 操作错误: {''.join(e.orig.args)}\n"
        )
    except Exception as e:
        if isinstance(e, SqliteWarning):
            logger.opt(raw=True, colors=True).warning(
                f"<yellow>W:</yellow> 数据库警告: {''.join(e.args)}\n"
            )
            return
        logger.exception("E: 数据库运行出错(db_execute)")
