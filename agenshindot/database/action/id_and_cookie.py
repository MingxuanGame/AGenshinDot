from typing import Dict
from http.cookies import SimpleCookie

from ..engine import get_db
from ..model.id_and_cookie import (
    Cookie,
    CookieOrm,
    CookieCache,
    PublicCookie,
    CookieCacheOrm,
    PublicCookieOrm,
)


async def get_cookie(uid: int) -> Dict[str, str]:
    db = get_db()
    if db:
        simple_cookie = SimpleCookie()

        if own_cookie := await db.select(CookieOrm, uid):
            cookie = Cookie.from_orm(own_cookie)
            raw = cookie.cookie
            if raw:
                simple_cookie.load(raw)
        if cache_cookie := await db.select(CookieCacheOrm, uid):
            cookie = CookieCache.from_orm(cache_cookie)
        else:
            other_cookies = list(
                await db.fetch(PublicCookieOrm, PublicCookieOrm.times < 30)
            )
            if not other_cookies:
                raise ValueError(f"No cookie for uid {uid}")
            cookie = PublicCookie.from_orm(other_cookies[0])
            await db.update(
                PublicCookieOrm,
                PublicCookieOrm.id == cookie.id,
                times=cookie.times + 1,
            )
            await db.insert_or_update(
                CookieCacheOrm,
                PublicCookieOrm.uid == uid,
                cookie=cookie.cookie,
            )
        simple_cookie.load(cookie.cookie)
        return {k: v.value for k, v in simple_cookie.items()}
    raise TypeError("Database is None")
