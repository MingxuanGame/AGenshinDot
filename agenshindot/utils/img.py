from __future__ import annotations

from io import BytesIO
from warnings import warn
from typing import Any, Tuple, Literal, Optional

from PIL import Image, ImageDraw
from aiohttp import ClientSession


def rectangle_to_round(img: Image.Image) -> Image.Image:
    # https://stackoverflow.com/questions/58543750/whats-the-most-simple-way-to-crop-a-circle-thumbnail-from-an-image
    width, height = img.size
    x = (width - height) // 2
    img_cropped = img.crop((x, 0, x + height, height))
    mask = Image.new("L", img_cropped.size)
    mask_draw = ImageDraw.Draw(mask)
    width, height = img_cropped.size
    mask_draw.ellipse((0, 0, width, height), fill=255)
    img_cropped.putalpha(mask)
    return img_cropped


def rectangle_to_rounded_rectangle(
    img: Image.Image, radius: int
) -> Image.Image:
    mask = Image.new("L", img.size)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        xy=(0, 0, *img.size),
        fill="#FFFFFF",
        width=img.size,  # type: ignore
        radius=radius,
    )
    img_cropped = img.crop((0, 0, *img.size))
    img_cropped.putalpha(mask)
    return img_cropped


def for_draw(
    img: Image.Image,
    interval: int,
    start: Tuple[int, int],
    *imgs: Image.Image,
    mode: Literal["row", "line"] = "row",
    next_line: Optional[int] = None,
    next_line_interval: Optional[int] = None,
    reversed: Optional[bool] = False,
) -> None:
    if next_line and mode == "line":
        warn("next_line is not available in `line` mode", UserWarning)
    if next_line and not next_line_interval:
        raise ValueError(
            "next_line_interval cannot be None when next_line is not None"
        )
    if reversed:
        interval = -interval
    x, y = start
    start_x = x
    for im in imgs:
        img.paste(im, (x, y), im)
        if mode == "row":
            x += interval
            if next_line and x >= next_line:
                x = start_x
                y += next_line_interval  # type: ignore
        else:
            y += interval


def for_text(
    img: Image.Image | ImageDraw.ImageDraw,
    interval: int,
    start: Tuple[int, int],
    *texts: str,
    mode: Literal["row", "line"] = "row",
    next_line: Optional[int] = None,
    next_line_interval: Optional[int] = None,
    reversed: Optional[bool] = False,
    **kwargs: Any,
) -> None:
    if next_line and mode == "line":
        warn("next_line is not available in `line` mode", UserWarning)
    if next_line and not next_line_interval:
        raise ValueError(
            "next_line_interval cannot be None when next_line is not None"
        )
    if reversed:
        interval = -interval
    x, y = start
    draw = ImageDraw.Draw(img) if isinstance(img, Image.Image) else img
    for t in texts:
        draw.text((x, y), t, **kwargs)
        if mode == "row":
            x += interval
            if next_line and x >= next_line:
                y += next_line_interval  # type: ignore
        else:
            y += interval
