import re
import traceback
from dataclasses import dataclass, field
from enum import Enum
from subprocess import check_output
from typing import Iterable, Optional, Iterator


class Rotation(str, Enum):
    NORMAL = "normal"
    INVERTED = "inverted"
    LEFT = "left"
    RIGHT = "right"

    def __repr__(self):
        return self.value


class Reflection(str, Enum):
    NORMAL = "normal"
    X = "x"
    Y = "y"
    XY = "xy"

    def __repr__(self):
        return self.value


@dataclass
class Mode:
    width: int
    height: int
    rate: float


@dataclass
class Output:
    name: str
    x: int
    y: int
    rotation: Rotation = Rotation.NORMAL
    reflection: Reflection = Reflection.NORMAL
    brightness: float = 1.0
    active: bool = False
    primary: bool = False
    modes: list[Mode] = field(default_factory=list)
    current_mode_index: Optional[int] = None
    preferred_mode_index: Optional[int] = None
    same_as: Optional[str] = None
    row: Optional[int] = None

    @property
    def _current_mode(self):
        if self.current_mode_index:
            idx = self.current_mode_index
        elif self.preferred_mode_index:
            idx = self.preferred_mode_index
        else:
            return None

        return self.modes[idx]

    @property
    def width(self):
        if cm := self._current_mode:
            return cm.width

    @property
    def height(self):
        if cm := self._current_mode:
            return cm.height

    @property
    def rate(self):
        if cm := self._current_mode:
            return cm.rate

    @property
    def blanked(self):
        return abs(self.brightness) < 1e-09


def query_outputs() -> Iterable[Output]:
    outputs = []
    xrandr_text = check_output(["xrandr", "--verbose"], universal_newlines=True)
    output_blocks = re.split(r"\n(?=\S)", xrandr_text, re.MULTILINE)
    info_pattern = re.compile(
        r"^(?P<name>\S+)"  # output name
        r" connected "  # must be connected
        r"(primary )?"  # check if primary output
        r"((?P<width>\d+)x(?P<height>\d+)\+(?P<X>\d+)\+(?P<Y>\d+) )?"  # width x height + xoffset + yoffset
        r"(\((?P<mode>\S+)\) )?"  # mode code (0x4a)
        r"(?P<rotation>normal|left|inverted|right)? ?"  # rotation
        r"(?P<reflection>X axis|Y axis|X and Y axis)?"
    )  # reflection
    brightness_pattern = re.compile(
        r"^\tBrightness: (?P<brightness>[\d.]+)", re.MULTILINE
    )
    for block in output_blocks:
        output = {}
        info_match = info_pattern.match(block)
        if info_match:
            groups = info_match.groupdict()
            output["name"] = groups["name"]

            if info_match.group(2):
                output["primary"] = True

            if info_match.group(3):
                output["active"] = True
                output["width"], output["height"], output["x"], output["y"] = map(
                    int, info_match.group(4, 5, 6, 7)
                )

            rotation = Rotation.NORMAL
            if "rotation" in groups:
                rot = groups["rotation"]
                if rot is not None:
                    rotation = Rotation(rot)
                if rotation in [Rotation.LEFT, Rotation.RIGHT]:
                    output["width"], output["height"] = (
                        output["height"],
                        output["width"],
                    )
                output["rotation"] = rotation

            reflection = Reflection.NORMAL
            if "reflection" in groups:
                ref = groups["reflection"]
                if ref == "X axis":
                    reflection = Reflection.X
                elif ref == "Y axis":
                    reflection = Reflection.Y
                elif ref == "X and Y axis":
                    reflection = Reflection.XY

            output["reflection"] = reflection

            brightness_match = brightness_pattern.search(block)
            if brightness_match:
                try:
                    brightness = float(brightness_match.group(1))
                    output["brightness"] = brightness
                except ValueError:
                    pass

            mode_pattern = re.compile(
                r"^  (?P<width>\d+)x(?P<height>\d+)[^\n]*?\n +h:[^\n]*?\n +v:[^\n]*?(?P<rate>[\d.]+)Hz$",
                re.MULTILINE,
            )
            mode_matches = mode_pattern.finditer(block)
            modes = []
            for i, mode_match in enumerate(mode_matches):
                if "*current" in mode_match.group(0):
                    output["current_mode_index"] = i
                    output["rate"] = mode_match.group(3)
                if "+preferred" in mode_match.group(0):
                    output["preferred_mode_index"] = i
                modes.append(Mode(*mode_match.group("width", "height", "rate")))
            output["modes"] = modes

            try:
                out = Output(**output)
                outputs.append(out)
            except Exception as e:
                traceback.print_exception(e)

    outputs.sort(key=lambda m: m.x if m.x is not None else -1)
    prev = None
    for output in outputs:
        if prev is not None and output.active and prev.active and output.x == prev.x:
            output.same_as = prev.name
        else:
            prev = output

    return outputs
