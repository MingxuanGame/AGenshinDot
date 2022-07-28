from pathlib import Path
from typing import Optional
from sys import exit as exit_
from traceback import print_exc

from tomlkit import load
from tomlkit.exceptions import UnexpectedCharError
from pydantic import BaseModel, ValidationError, validator
from graia.ariadne.connection.config import (
    HttpClientConfig,
    HttpServerConfig,
    WebsocketClientConfig,
    WebsocketServerConfig,
)


class Config(BaseModel):
    account: int
    """QQ 号"""
    verify_key: str
    """鉴权密钥"""
    enable_console: bool = True
    """是否启用控制台"""

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
