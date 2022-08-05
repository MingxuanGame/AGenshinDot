from __future__ import annotations

from io import BytesIO
from pathlib import Path
from textwrap import wrap
from asyncio import gather, create_task
from typing import Dict, List, Optional

from graia.ariadne.util.async_exec import cpu_bound
from aiohttp import ClientSession, ClientResponseError
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ...version import __version__
from ...utils.mihoyo_bbs.model.base import Info
from ...utils.minigg.character import CharacterClient
from ...utils.minigg.model.character import Character
from ...utils.img import (
    for_draw,
    for_text,
    rectangle_to_round,
    rectangle_to_rounded_rectangle,
)

RESOURCE_PATH = Path(__file__).parent.parent.parent / "resource" / "mihoyo_bbs"
COLORS: Dict[str, str] = {
    "Electro": "#CBA6FF",
    "Hydro": "#A1A1ED",
    "Cryo": "#A6DBFF",
    "Anemo": "#8BE0D6",
    "Geo": "#DECF62",
    "Pyro": "#FF8A8A",
    "Dendro": "#ACDE62",
}
ELEMENTS: Dict[str, str] = {
    "Electro": "雷",
    "Hydro": "水",
    "Cryo": "冰",
    "Anemo": "风",
    "Geo": "岩",
    "Pyro": "火",
    "Dendro": "草",
}


async def download_image(url: str) -> Image.Image:
    async with ClientSession() as session:
        resp = await session.get(url)
        resp.raise_for_status()
        if resp.url == "https://upload-bbs.mihoyo.com/404.png":
            raise ClientResponseError(
                resp.request_info,
                resp.history,
                status=404,
                message="Not Found",
            )
        return Image.open(BytesIO(await resp.read()))


async def draw_info(
    uid: int, data: Info, avatar: BytesIO, name: Optional[str] = None
) -> BytesIO:  # sourcery skip: low-code-quality
    if not name:
        name = data.role.nickname
    img = Image.new("RGBA", (455 * 2, 750 * 2), (239, 234, 229))
    draw = ImageDraw.Draw(img)
    font_8 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 8)
    font_15 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 15)
    font_16 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 16)
    font_18 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 18)
    font_16 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 16)
    font_24 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 24)
    font_30 = ImageFont.truetype(str(RESOURCE_PATH / "HYWH85W.ttf"), 30)

    # 基础信息
    avatar_round = rectangle_to_round(Image.open(avatar)).resize(
        (74 * 2, 74 * 2)
    )
    draw.rounded_rectangle(
        xy=(92 * 2, 61 * 2, 321 * 2, 111 * 2),
        fill="#F1DB9A",
        width=(229 * 2, 50 * 2),  # type: ignore
        radius=20,
    )

    img.paste(avatar_round, (37 * 2, 47 * 2), avatar_round)
    draw.text((121 * 2, 68 * 2), name, fill="#000000", font=font_24)
    draw.text(
        (242 * 2, 68 * 2),
        f"(Lv. {data.role.level})",
        fill="#66871E",
        font=font_24,
    )

    draw.text((121 * 2, 88 * 2), f"UID: {uid}", fill="#000000", font=font_24)
    draw.rounded_rectangle(
        (32 * 2, 139 * 2, 321 * 2, 424 * 2),
        fill="#F1DB9A",
        width=(289 * 2, 285 * 2),  # type: ignore
        radius=20,
    )

    goto = Image.open(RESOURCE_PATH / "goto.png").resize((22 * 2, 22 * 2))
    img.paste(goto, (48 * 2, 156 * 2), goto)
    draw.text((70 * 2, 160 * 2), "基础信息", fill="#000000", font=font_30)
    for_text(
        draw,
        24 * 2,
        (52 * 2, 178 * 2),
        f"活跃天数 {data.stats.active_day_number}",
        f"成就达成 {data.stats.achievement_number}",
        f"角色总数 {data.stats.avatar_number}",
        f"解锁传送点 {data.stats.way_point_number}",
        f"解锁秘境 {data.stats.domain_number}",
        f"深境螺旋 {data.stats.spiral_abyss}",
        mode="line",
        fill="#11965A",
        font=font_24,
    )

    chest = Image.open(RESOURCE_PATH / "chest.png").resize((22 * 2, 22 * 2))
    img.paste(chest, (186 * 2, 156 * 2), chest)
    draw.text((208 * 2, 160 * 2), "宝箱信息", fill="#000000", font=font_30)
    for_text(
        draw,
        24 * 2,
        (186 * 2, 178 * 2),
        f"华丽宝箱 {data.stats.luxurious_chest_number}",
        f"珍贵宝箱 {data.stats.precious_chest_number}",
        f"精致宝箱 {data.stats.exquisite_chest_number}",
        f"普通宝箱 {data.stats.common_chest_number}",
        f"奇馈宝箱 {data.stats.magic_chest_number}",
        mode="line",
        fill="#11965A",
        font=font_24,
    )

    draw.rounded_rectangle(
        (62 * 2, 336 * 2, 292 * 2, 413 * 2),
        fill="#FFEDB0",
        width=(237 * 2, 77 * 2),  # type: ignore
        radius=20,
    )

    for_draw(
        img,
        87 * 2,
        (67 * 2, 340 * 2),
        Image.open(RESOURCE_PATH / "anemoculus.png").resize((41 * 2, 48 * 2)),
        Image.open(RESOURCE_PATH / "geoculus.png").resize((41 * 2, 48 * 2)),
        Image.open(RESOURCE_PATH / "electroculus.png").resize(
            (41 * 2, 48 * 2)
        ),
    )

    for_text(
        draw,
        87 * 2,
        (88 * 2, 401 * 2),
        f"{data.stats.anemoculus_number}/66",
        f"{data.stats.geoculus_number}/131",
        f"{data.stats.electroculus_number}/181",
        mode="row",
        fill="#544F21",
        font=font_24,
        anchor="mm",
    )

    # 角色信息
    def search_name(id: int, name: str):
        if id == 10000005:
            return "空"
        elif id == 10000007:
            return "荧"
        else:
            return name

    avatars = data.avatars[:8]
    avatar_cards: List[Image.Image] = await gather(
        *[create_task(download_image(char.card_image)) for char in avatars]
    )
    cards: List[Image.Image] = []
    client = CharacterClient()
    char_data_list: List[Character] = await gather(
        *[
            create_task(client.get_info(search_name(char.id, char.name)))
            for char in avatars
        ]
    )

    star = Image.open(RESOURCE_PATH / "star.png").resize((14 * 2, 14 * 2))
    for i, char in enumerate(avatars):
        card = Image.new("RGBA", (143 * 2, 68 * 2), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card)
        card_draw.rounded_rectangle(
            (0, 0, 143 * 2, 68 * 2),
            fill=COLORS[char.element],
            width=(145 * 2, 68 * 2),  # type: ignore
            radius=16,
        )

        avatar_card = avatar_cards[i].resize((60 * 2, 60 * 2))
        card.paste(avatar_card, (0 * 2, 4 * 2), avatar_card)
        avatar_ = avatars[i]
        card_draw.text(
            (58 * 2, 8 * 2),
            f"{avatar_.name} (Lv. {avatar_.level})",
            font=font_16,
            fill="#000000",
        )

        for_draw(card, 16 * 2, (56 * 2, 20 * 2), *[star] * avatar_.rarity)
        fetter = Image.open(RESOURCE_PATH / "fetter.png").resize(
            (10 * 2, 8 * 2)
        )
        card.paste(fetter, (57 * 2, 38 * 2), fetter)
        card_draw.text(
            (68 * 2, 37 * 2),
            f"好感 {avatar_.fetter}",
            font=font_15,
            fill="#000000",
        )

        constellation = Image.open(RESOURCE_PATH / "constellation.png").resize(
            (12 * 2, 12 * 2)
        )

        card.paste(constellation, (94 * 2, 35 * 2), constellation)
        card_draw.text(
            (105 * 2, 37 * 2),
            f"命座 {avatar_.actived_constellation_num}",
            font=font_15,
            fill="#000000",
        )

        char_data = char_data_list[i]
        card_draw.text(
            (115, 47 * 2),
            (
                f"{ELEMENTS[char.element]} / {char_data.region or '无'} "
                f"/ {char_data.weapon_type} / {char_data.constellation}"
            ),
            font=font_8,
            fill="#545454",
        )

        descriptions = wrap(char_data.description, width=20)
        if len(descriptions) >= 2:
            description_1 = descriptions[1]
            if len(description_1) > 19:
                descriptions[1] = f"{description_1[:19]}..."
            if description_1[0] == "。":
                descriptions[1] = ""
        card_draw.text(
            (115, 54 * 2),
            "\n".join(descriptions),
            font=font_8,
            fill="#545454",
        )

        cards.append(card)
    for_draw(
        img,
        144 * 2,
        (32 * 2, 435 * 2),
        *cards,
        mode="row",
        next_line=180 * 2,
        next_line_interval=77 * 2,
    )

    # 世界信息
    worlds = sorted(data.world_explorations, key=lambda x: x.id)
    world_imgs: List[Image.Image] = []
    world_icons: List[Image.Image] = await gather(
        *[create_task(download_image(world.icon)) for world in worlds]
    )

    offering_icon_url_map: Dict[int, str] = {
        world.id: world.offerings[0].icon
        for world in worlds
        if world.offerings
    }

    offering_icons: List[Image.Image] = await gather(
        *[
            create_task(download_image(url))
            for url in offering_icon_url_map.values()
        ]
    )

    offering_icon_map: Dict[int, Image.Image] = {
        k: offering_icons[i]
        for i, k in enumerate(offering_icon_url_map.keys())
    }
    del offering_icon_url_map, offering_icons
    for i, world in enumerate(worlds):
        card = Image.new("RGBA", (94 * 2, 50 * 2), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card)
        card_draw.rounded_rectangle(
            (0, 0, 94 * 2, 50 * 2),
            fill="#CFA972",
            width=(94 * 2, 50 * 2),  # type: ignore
            radius=12,
        )

        world_icon = world_icons[i].resize((43 * 2, 43 * 2))
        card.paste(world_icon, (4 * 2, 4 * 2), world_icon)
        if not world.offerings:
            card_draw.text(
                (47 * 2, 16 * 2),
                f"{world.exploration_percentage / 10}%",
                font=font_16,
                fill="#000000",
            )

            card_draw.text(
                (47 * 2, 28 * 2),
                f"Lv. {world.level}",
                font=font_16,
                fill="#000000",
            )

        else:
            card_draw.text(
                (47 * 2, 9 * 2),
                f"{world.exploration_percentage / 10}%",
                font=font_16,
                fill="#000000",
            )

            card_draw.text(
                (47 * 2, 20 * 2),
                f"Lv. {world.level}",
                font=font_16,
                fill="#000000",
            )

            offering = offering_icon_map[world.id].resize((10 * 2, 10 * 2))
            card.paste(offering, (47 * 2, 33 * 2), offering)
            card_draw.text(
                (58 * 2, 34 * 2),
                f"Lv. {world.offerings[0].level}",
                font=font_16,
                fill="#000000",
            )

        world_imgs.append(card)
    for_draw(img, 56 * 2, (334 * 2, 71 * 2), *world_imgs, mode="line")

    # 尘歌壶信息
    homes = data.homes
    tasks = [create_task(download_image(home.icon)) for home in homes] + [
        create_task(download_image(home.comfort_level_icon)) for home in homes
    ]
    home_icons: List[Image.Image] = await gather(*tasks)
    home_imgs: List[Image.Image] = []
    for i, home in enumerate(homes):
        rounded_blur_icon = rectangle_to_rounded_rectangle(
            home_icons[i].resize((95 * 2, 58 * 2)), 14 * 2
        ).filter(ImageFilter.GaussianBlur(radius=1))
        card_draw = ImageDraw.Draw(rounded_blur_icon)
        card_draw.text((9 * 2, 7 * 2), home.name, font=font_18, fill="#000000")
        level_icon = home_icons[i + len(homes)].resize((16 * 2, 16 * 2))
        rounded_blur_icon.paste(level_icon, (5 * 2, 20 * 2), level_icon)
        card_draw.text(
            (21 * 2, 21 * 2),
            f"{home.comfort_level_name}({home.comfort_num})",
            font=font_18,
            fill="#000000",
        )

        visitor = Image.open(RESOURCE_PATH / "visitor.png").resize(
            (16 * 2, 16 * 2)
        )
        rounded_blur_icon.paste(visitor, (5 * 2, 36 * 2), visitor)
        card_draw.text(
            (21 * 2, 38 * 2),
            str(home.visit_num),
            font=font_18,
            fill="#000000",
        )

        visitor = Image.open(RESOURCE_PATH / "currency.png").resize(
            (16 * 2, 16 * 2)
        )
        rounded_blur_icon.paste(visitor, (45 * 2, 36 * 2), visitor)
        card_draw.text(
            (61 * 2, 38 * 2),
            str(home.item_num),
            font=font_18,
            fill="#000000",
        )
        home_imgs.append(rounded_blur_icon)
    for_draw(
        img,
        67 * 2,
        (334 * 2, 675 * 2),
        *home_imgs,
        mode="line",
        reversed=True,
    )

    # 版本与机器人信息
    draw.text(
        (300 * 2, 738 * 2),
        f"MingxuanGame | AGenshinDot {__version__}",
        font=font_15,
        fill="#878686",
    )

    # 保存图片
    # img.show()
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio
