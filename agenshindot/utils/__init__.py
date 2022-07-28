from .minigg import Lang as Lang
from .minigg.weapon import WeaponClient as WeaponClient
from .msg import send_msg_auto_forward as send_msg_auto_forward
from .minigg.character import CharacterClient as CharacterClient

__all__ = ["minigg", "msg"]
