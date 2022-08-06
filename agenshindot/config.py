from pathlib import Path
from typing import Optional
from sys import exit as exit_
from datetime import timedelta
from traceback import print_exc

from tomlkit import load
from tomlkit.exceptions import UnexpectedCharError
from pydantic import Field, BaseModel, ValidationError, validator
from graia.ariadne.connection.config import (
    HttpClientConfig,
    HttpServerConfig,
    WebsocketClientConfig,
    WebsocketServerConfig,
)

from .typing import LogLevel


class LogConfig(BaseModel):
    expire_time: timedelta = timedelta(weeks=2)
    """日志过期时间，过期即删除"""
    level: LogLevel = "INFO"
    """日志等级"""
    db_log: bool = False
    """数据库日志"""


class Config(BaseModel):
    account: int
    """QQ 号"""
    verify_key: str
    """鉴权密钥"""
    enable_console: bool = True
    """是否启用控制台"""
    log: LogConfig = Field(default_factory=LogConfig)
    """日志配置"""
    db_url: str = "sqlite+aiosqlite:///agenshindot.db"
    """数据库 URL"""
    enable_bind_cookie: bool = False
    """启用 cookie 绑定"""
    send_message_to_binder: bool = True
    """Cookie 失效时是否向 Cookie 绑定者反馈信息"""

    ws: Optional[WebsocketClientConfig] = None
    """正向 WebSocket"""
    ws_reverse: Optional[WebsocketServerConfig] = None
    """反向 WebSocket"""
    http: Optional[HttpClientConfig] = None
    """HTTP 客户端"""
    webhook: Optional[HttpServerConfig] = None
    """HTTP Webhook"""

    @validator("ws", "http", pre=True)
    def check_forward(cls, v):
        return (v,) if isinstance(v, str) else v

    @validator("ws_reverse", pre=True)
    def check_ws_server(cls, v):
        if isinstance(v, dict):
            return tuple(v.values())
        elif isinstance(v, str):
            if not v:
                raise ValueError("path is empty")
            return (v, {}, {})
        return v

    @validator("webhook", pre=True)
    def check_webhook(cls, v):
        if isinstance(v, dict):
            return tuple(v.values())
        elif isinstance(v, str):
            if not v:
                raise ValueError("path is empty")
            return (v, {})
        return v


def load_config() -> Config:
    config_path = Path() / "config.toml"
    if not config_path.is_file():
        print("E: 未在当前目录找到 config.toml，请按照文档新建配置文件")
        exit_(1)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return Config.parse_obj(load(f))
    except OSError as e:
        print(f"E: 读取文件时出错：{e}")
    except UnexpectedCharError as e:
        print(f"E: 反序列化 TOML 时出错：{e}")
    except ValidationError as e:
        print(f"E: 解析配置文件时出错：{e}")
    except Exception:
        print("E: 出现未知错误，请将错误报告提交给开发者处理")
        print_exc()
    exit_(1)
