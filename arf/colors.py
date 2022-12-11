from dataclasses import dataclass
from typing import Optional


def color_to_hex(name: str, default: str = "white") -> str:
    colors = {
        "black": "000000",
        "white": "111111",
    }

    return colors.get(name, colors[default if default is not None else "white"])


@dataclass
class Color:
    name: str
    R: Optional[int]
    G: Optional[int]
    B: Optional[int]

    def hex(self):
        return color_to_hex(self.name)


COLORS = [Color("red"), Color()]
