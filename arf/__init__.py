import os
from pathlib import Path

from xdg.BaseDirectory import xdg_config_home

from arf.peripherals.monitor import query_outputs

SELF_DIRECTORY = Path(__file__).parent.absolute()

DEFAULT_CONFIG_FILE = os.getenv(
    "ARF_ROOT", Path(xdg_config_home) / "arf" / "widgets.yaml"
)


def read_config(file: str | Path):
    file = Path(file)

    if file.exists():
        print(f"file {file} exists")
    print(f"file {file} does not exist")


def start(config: str, widget: str):
    read_config(config)

    print(f"starting {widget}")

    print(query_outputs())
