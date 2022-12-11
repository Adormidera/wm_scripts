from tkinter import Tk
from typing import Any, Mapping

from arf.peripherals import OutputManager
from arf.peripherals.monitor.manager import Symbol

from . import Widget


class MonitorManager(Widget):
    NOOP_SYMBOL = Symbol.desktop

    def get_plugin(self, root: Tk, **kwargs):
        return OutputManager

    def plugin_params(self) -> Mapping[str, Any]:
        return {}
