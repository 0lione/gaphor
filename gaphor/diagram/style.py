from typing import Dict, Optional, Sequence, Tuple

import tinycss2.color3
from typing_extensions import TypedDict

from gaphor.core.styling import StyleDeclarations
from gaphor.diagram.text import (
    FontStyle,
    FontWeight,
    TextAlign,
    TextDecoration,
    VerticalAlign,
)

Color = Tuple[float, float, float, float]  # RGBA
Padding = Tuple[float, float, float, float]

# Style is using SVG properties where possible
# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute
Style = TypedDict(
    "Style",
    {
        "padding": Padding,
        "min-width": float,
        "min-height": float,
        "line-width": float,
        "vertical-spacing": float,
        "border-radius": float,
        "background-color": Optional[Color],
        "font-family": str,
        "font-size": float,
        "font-style": FontStyle,
        "font-weight": Optional[FontWeight],
        "text-decoration": Optional[TextDecoration],
        "text-align": TextAlign,
        "text-color": Optional[Color],
        "color": Optional[Color],
        "vertical-align": VerticalAlign,
        "dash-style": Sequence[float],
        "highlight-color": Optional[Color],
        # CommentItem:
        "ear": int,
    },
    total=False,
)


def _clip_color(c):
    if c < 0:
        return 0
    if c > 1:
        return 1
    return c


@StyleDeclarations.register(
    "background-color", "color", "highlight-color", "text-color"
)
def parse_color(prop, value):
    color = tinycss2.color3.parse_color(value)
    return tuple(_clip_color(v) for v in color) if color else None


@StyleDeclarations.register(
    "min-width",
    "min-height",
    "line-width",
    "vertical-spacing",
    "border-radius",
    "font-size",
)
def parse_positive_number(prop, value) -> Optional[float]:
    if isinstance(value, float) and value > 0:
        return value
    return None


@StyleDeclarations.register("padding")
def parse_padding(prop, value) -> Optional[Padding]:
    if isinstance(value, float):
        return (value, value, value, value)
    n = len(value)
    if not n or any(not isinstance(v, float) for v in value):
        return None

    return (
        value[0],
        value[1],
        value[2] if n > 2 else value[0],
        value[3] if n > 3 else value[1],
    )


@StyleDeclarations.register("dash-style")
def parse_sequence_numbers(prop, value) -> Optional[Sequence[float]]:
    if isinstance(value, float):
        return (value,)
    elif all(isinstance(v, float) for v in value):
        return value  # type: ignore[no-any-return]
    return None


enum_styles: Dict[str, Dict[str, object]] = {
    "font-style": {e.value: e for e in FontStyle},
    "font-weight": {e.value: e for e in FontWeight},
    "text-decoration": {e.value: e for e in TextDecoration},
    "text-align": {e.value: e for e in TextAlign},
    "vertical-align": {e.value: e for e in VerticalAlign},
}


@StyleDeclarations.register(*enum_styles.keys())
def parse_enum(prop, value):
    return enum_styles[prop].get(value)
