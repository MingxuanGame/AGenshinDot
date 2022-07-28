from pathlib import Path
from pkgutil import iter_modules

from creart import create
from loguru import logger
from graia.saya import Saya
from graia.ariadne.app import Ariadne
from graia.broadcast import Broadcast
from prompt_toolkit.styles import Style
from graia.ariadne.console import Console
from prompt_toolkit.formatted_text import HTML
from graia.ariadne.connection.config import config
from graia.ariadne.console.saya import ConsoleBehaviour

from .config import load_config
from .version import __version__

ags_config = load_config()
ags_config_dict = load_config().dict(exclude_none=True)
ags_config_dict.pop("account")
ags_config_dict.pop("enable_console")
ags_config_dict.pop("verify_key")

bcc = create(Broadcast)
saya = create(Saya)
app = Ariadne(
    connection=config(
        ags_config.account, ags_config.verify_key, *ags_config_dict.values()
    ),
)
if ags_config.enable_console:
    con = Console(
        broadcast=bcc,
        prompt=HTML(f"<name>AGenshinDot</name>(<ver>{__version__}</ver>)> "),
        style=Style(
            [
                ("name", "fg:#61afef"),
                ("ver", "fg:#0ed145"),
            ]
        ),
    )
    saya.install_behaviours(ConsoleBehaviour(con))


with saya.module_context():
    for module_info in iter_modules([str(Path(__file__).parent / "modules")]):
        if not module_info.name.startswith("_"):
            if (
                not ags_config.enable_console
            ) and module_info.name == "console":
                continue
            module_name = f"agenshindot.modules.{module_info.name}"
            saya.require(module_name)


def main():
    logger.info("AGenshinDot 是 GenshinDot 的 Python 实现")
    logger.opt(colors=True).info("<green>Powered by Graia-Ariadne</green>")
    logger.opt(colors=True).info(
        "AGenshinDot 遵循 <y>GNU AGPLv3</y> 许可协议开放全部源代码",
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
    logger.info("AGenshinDot 已关闭")
