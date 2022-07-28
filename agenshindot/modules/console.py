from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch

from ..version import __version__

saya = Saya.current()
channel = Channel.current()

LOGO = r"""
           _____                _     _       _____        _
     /\   / ____|              | |   (_)     |  __ \      | |
    /  \ | |  __  ___ _ __  ___| |__  _ _ __ | |  | | ___ | |_
   / /\ \| | |_ |/ _ \ '_ \/ __| '_ \| | '_ \| |  | |/ _ \| __|
  / ____ \ |__| |  __/ | | \__ \ | | | | | | | |__| | (_) | |_
 /_/    \_\_____|\___|_| |_|___/_| |_|_|_| |_|_____/ \___/ \__|
"""


@channel.use(ConsoleSchema([Twilight(FullMatch("/stop"))]))
async def stop(app: Ariadne, con: Console):
    con.stop()
    app.stop()


@channel.use(ConsoleSchema([Twilight(FullMatch("/license"))]))
async def license():
    logger.opt(raw=True, colors=True).info(
        "AGenshinDot 遵循 <y>GNU AGPLv3</y> 许可协议开放全部源代码\n"
    )
    logger.opt(raw=True, colors=True).info(
        "你可以在 "
        "<blue>https://github.com/MingxuanGame/AGenshinDot/blob/master/LICENSE</blue>"
        " 找到本项目的许可证\n"
    )


@channel.use(ConsoleSchema([Twilight(FullMatch("/version"))]))
async def ver():
    logger.opt(raw=True, colors=True).info(f"<cyan>{LOGO}</cyan>\n")
    logger.opt(raw=True, colors=True).info(
        f"<magenta>AGenshinDot</magenta>: <green>{__version__}</green>\n"
    )
