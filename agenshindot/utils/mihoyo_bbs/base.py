from typing import Any, Dict, Mapping, cast

from yarl import URL

from .request import StatusError, request
from .model.base import Info, CNAccounts, OSAccounts

SERVER = {
    "1": "cn_gf01",
    "2": "cn_gf01",
    "5": "cn_qd01",
    "6": "os_usa",
    "7": "os_euro",
    "8": "os_asia",
    "9": "os_cht",
}

OS_GAME_RECORD_URL = URL("/game_record/")
CN_GAME_RECORD_URL = URL("/game_record/app/")


def get_server(uid: int) -> str:
    start = str(uid)
    if len(start) != 9 or len(start) == 9 and not SERVER.get(start[0]):
        raise ValueError("UID is invalid")
    return SERVER.get(start[0], "")


def is_os(uid: int) -> bool:
    return str(uid)[0] not in ["1", "2", "5"]


async def get_info(uid: int, cookie: Mapping[str, str]) -> Info:
    server = get_server(uid)
    os = is_os(uid)
    data = await request(
        endpoint=str(
            (OS_GAME_RECORD_URL if os else CN_GAME_RECORD_URL)
            / "genshin/api/index"
        ),
        cookie=cookie,
        method="GET",
        os=os,
        params={"role_id": uid, "server": server},
    )
    return Info.parse_obj(data)


async def get_account(cookie: Mapping[str, str]) -> CNAccounts | OSAccounts:
    mihoyo_id = cookie.get("account_id") or cookie.get("ltuid")
    if not mihoyo_id:
        raise ValueError("Cookie hasn't mihoyo bbs account number")
    try:
        data = cast(
            Dict[str, Any],
            await request(
                endpoint="/binding/api/getUserGameRolesByCookie",
                cookie=cookie,
                method="GET",
                os=False,
                old=True,
            ),
        )
        data["mihoyo_id"] = int(mihoyo_id)
        return CNAccounts.parse_obj(data)
    except StatusError:
        data = cast(
            Dict[str, Any],
            await request(
                endpoint="/game_record/card/wapi/getGameRecordCard",
                cookie=cookie,
                method="GET",
                os=True,
                params={"uid": mihoyo_id, "gids": 2},
            ),
        )
        data["mihoyo_id"] = int(mihoyo_id)
        return OSAccounts.parse_obj(data)
