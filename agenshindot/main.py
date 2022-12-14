from pathlib import Path
from pkgutil import iter_modules
from asyncio import get_event_loop

from creart import create
from loguru import logger
from graia.saya import Saya
from graia.ariadne.app import Ariadne
from graia.broadcast import Broadcast
from prompt_toolkit.styles import Style
from graia.ariadne.console import Console
from prompt_toolkit.formatted_text import HTML
from graia.ariadne.connection.config import config
from graia.ariadne.message.commander import Commander
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.message.commander.saya import CommanderBehaviour

from .log import patch_logger
from .config import load_config
from .version import __version__
from .database.engine import close, get_db, init_db


def main():

    ags_config = load_config()

    bcc = create(Broadcast)
    cmd = create(Commander)
    saya = create(Saya)
    app = Ariadne(
        connection=config(
            ags_config.account,
            ags_config.verify_key,
            *[
                config
                for config in (
                    ags_config.http,
                    ags_config.ws,
                    ags_config.webhook,
                    ags_config.ws_reverse,
                )
                if config
            ],
        ),
    )
    saya.install_behaviours(CommanderBehaviour(cmd))

    patch_logger(
        ags_config.log.level,
        ags_config.log.expire_time,
        not ags_config.enable_console,
        ags_config.log.db_log,
    )

    if ags_config.enable_console:
        con = Console(
            broadcast=bcc,
            prompt=HTML(
                f"<name>AGenshinDot</name>(<ver>{__version__}</ver>)> "
            ),
            style=Style(
                [
                    ("name", "fg:#61afef"),
                    ("ver", "fg:#0ed145"),
                ]
            ),
        )
        saya.install_behaviours(ConsoleBehaviour(con))

    saya.install_behaviours(CommanderBehaviour(cmd))

    with saya.module_context():
        for module_info in iter_modules(
            [str(Path(__file__).parent / "modules")]
        ):
            if not module_info.name.startswith("_"):
                if (
                    not ags_config.enable_console
                ) and module_info.name == "console":
                    continue
                module_name = f"agenshindot.modules.{module_info.name}"
                saya.require(module_name)

    @bcc.receiver(ApplicationLaunched)
    async def _(app: Ariadne):
        try:
            init_db(ags_config.db_url, ags_config.log.db_log)
            db = get_db()
            if db:
                await db.create_tables()
                return
            else:
                logger.critical("?????????????????????????????????")
        except Exception:
            logger.exception("?????????????????????????????????")
        app.stop()

    logger.info("AGenshinDot ??? GenshinDot ??? Python ??????")
    logger.opt(colors=True).info("<green>Powered by Graia-Ariadne</green>")
    logger.opt(colors=True).info(
        "AGenshinDot ?????? <y>GNU AGPLv3</y> ?????????????????????????????????",
    )
    logger.opt(colors=True).info(
        "GenshinDot: <blue>https://github.com/MingxuanGame/GenshinDot</blue>"
    )
    logger.opt(colors=True).info(
        "AGenshinDot: <blue>https://github.com/MingxuanGame/AGenshinDot</blue>"
    )
    try:
        app.launch_blocking()
    except KeyboardInterrupt:
        app.stop()
    get_event_loop().run_until_complete(close())
    logger.info("AGenshinDot ?????????")
