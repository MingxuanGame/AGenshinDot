from typing import List
from datetime import datetime

from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Forward, ForwardNode


async def send_msg_auto_forward(
    app: Ariadne, group: Group, chain: MessageChain | List[MessageChain]
):
    if isinstance(chain, list):
        await app.send_message(
            group,
            Forward(
                [
                    ForwardNode(
                        target=app.account,
                        time=datetime.now(),
                        message=i,
                        name="AGenshinDot",
                    )
                    for i in chain
                ]
            ),
        )
    else:
        await app.send_message(group, chain)
