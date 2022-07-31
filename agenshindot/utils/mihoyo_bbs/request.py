from __future__ import annotations

from time import time
from json import dumps
from hashlib import md5
from string import ascii_letters
from random import choices, randint
from typing import Any, Dict, List, Literal, Mapping, Optional

from yarl import URL
from aiohttp import ClientSession

OS_DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
CN_DS_SALT = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
CN_API = URL("https://api-takumi-record.mihoyo.com")
OS_API = URL("https://bbs-api-os.hoyoverse.com")
CN_VERSION = "2.11.1"
CN_TYPE = "5"
OS_VERSION = "1.5.0"
OS_TYPE = "4"


class StatusError(ValueError):
    def __init__(self, status: int, *args: object) -> None:
        super().__init__(status, *args)
        self.status = status

    def __str__(self) -> str:
        return f"Mihoyo API status error: {self.status}"

    def __repr__(self) -> str:
        return f"<StatusError status={self.status}>"


def _md5(self) -> str:
    return md5(self.encode()).hexdigest()


def cn_ds_generator(
    body: Any = None, query: Optional[Mapping[str, Any]] = None
) -> str:
    t = int(time())
    r = randint(100001, 200000)
    b = dumps(body) if body else ""
    q = "&".join(f"{k}={v}" for k, v in sorted(query.items())) if query else ""

    h = _md5(f"salt={CN_DS_SALT}&t={t}&r={r}&b={b}&q={q}")
    return f"{t},{r},{h}"


def os_ds_generator() -> str:
    t = int(time())
    r = "".join(choices(ascii_letters, k=6))
    h = _md5(f"salt={OS_DS_SALT}&t={t}&r={r}")
    return f"{t},{r},{h}"


async def request(
    endpoint: str,
    cookie: Mapping[str, str],
    method: Literal["GET", "POST"] = "GET",
    os: bool = False,
    json: Optional[Mapping[str, Any]] = None,
    params: Optional[Mapping[str, str | int]] = None,
    **kwargs: Any,
) -> List[Any] | Dict[str, Any]:
    async with ClientSession(
        base_url=OS_API if os else CN_API,
        headers={
            "ds": os_ds_generator() if os else cn_ds_generator(json, params),
            "x-rpc-app_version": OS_VERSION if os else CN_VERSION,
            "x-rpc-client_type": OS_TYPE if os else CN_TYPE,
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 "
                "like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "miHoYoBBS/2.11.1"
            ),
            "Referer": "https://webstatic.mihoyo.com/",
        },
        cookies=cookie,
    ) as session:
        if method == "GET":
            kwargs = dict(kwargs, params=params)
        else:
            kwargs = dict(kwargs, json=json)
        resp = await session.request(method, endpoint, **kwargs)
        resp.raise_for_status()
        data = await resp.json()
        if data["retcode"] != 0:
            raise StatusError(data["retcode"])
        return data["data"]
