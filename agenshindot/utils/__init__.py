from typing import Dict
from http.cookies import SimpleCookie

from .minigg import Lang as Lang
from .minigg.weapon import WeaponClient as WeaponClient
from .msg import send_msg_auto_forward as send_msg_auto_forward
from .minigg.character import CharacterClient as CharacterClient


def cookie_str_to_mapping(cookie: str) -> Dict[str, str]:
    simple_cookie = SimpleCookie()
    simple_cookie.load(cookie)
    return {k: v.value for k, v in simple_cookie.items()}


__all__ = ["minigg", "msg"]
