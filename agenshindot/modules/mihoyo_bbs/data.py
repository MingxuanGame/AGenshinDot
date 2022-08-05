from __future__ import annotations

from io import BytesIO
from typing import Dict, Optional

from loguru import logger
from pydantic import ValidationError
from aiohttp import ClientResponseError, ClientConnectorError

from agenshindot.utils.mihoyo_bbs.base import get_info
from agenshindot.modules.mihoyo_bbs.draw import draw_info
from agenshindot.utils.mihoyo_bbs.request import StatusError
from agenshindot.database.action import get_cookie as get_cookie_db


async def get_cookie(uid: int) -> Dict[str, str] | str:
    try:
        result = await get_cookie_db(uid)
        return result
    except TypeError:
        return "E: 数据库未开启，请联系机器人管理员"
    except ValueError:
        return "E: 当前未找到 cookie，请稍后再试"
    except Exception as e:
        logger.exception("Error at get_cookie")
        return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"


async def draw(
    uid: int,
    cookie: Dict[str, str],
    avatar: bytes,
    nickname: Optional[str] = None,
) -> BytesIO | str:
    try:
        data = await get_info(uid, cookie)
        try:
            return await draw_info(uid, data, BytesIO(avatar), nickname)
        except ClientConnectorError as e:
            return f"E: 无法访问 米游社资源 API - {e.strerror}"
        except ClientResponseError as e:
            return f"E: 米游社资源 API HTTP 状态码异常 - {e.code} {e.message}"
        except Exception as e:
            logger.exception("Error at draw(draw_info)")
            return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"
    except StatusError as e:
        return f"E: 米游社状态异常: {e.status}"
    except ValidationError as e:
        return f"E: 解析数据出现异常:\n{e}"
    except ClientConnectorError as e:
        return f"E: 无法访问 米游社 API - {e.strerror}"
    except ClientResponseError as e:
        return f"E: 米游社 API HTTP 状态码异常 - {e.code} {e.message}"
    except Exception as e:
        logger.exception("Error at draw(draw_info)")
        return f"E: 出现未知错误，请将此错误提交给开发者处理 - {e}"
