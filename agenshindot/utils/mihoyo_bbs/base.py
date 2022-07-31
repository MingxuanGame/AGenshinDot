from typing import Mapping

from yarl import URL

from .model.base import Info
from .request import request

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


async def get_info(uid: int, cookie: Mapping[str, str]) -> Info:
    start = str(uid)
    if len(start) != 9 or len(start) == 9 and not SERVER.get(start[0]):
        raise ValueError("UID is invalid")
    server = SERVER.get(start[0], "")
    is_os = start[0] not in ["1", "2", "5"]
    data = await request(
        endpoint=str(
            (OS_GAME_RECORD_URL if is_os else CN_GAME_RECORD_URL)
            / "genshin/api/index"
        ),
        cookie=cookie,
        method="GET",
        os=is_os,
        params={"role_id": uid, "server": server},
    )
    return Info.parse_obj(data)
