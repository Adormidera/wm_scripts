import os
import sys
from abc import ABC, abstractmethod
from functools import cached_property, partial
from tkinter import Event, Tk, ttk
from typing import Any, Iterable, Mapping, Tuple


def split_camel_case(src) -> Iterable[str]:
    """
    Split a camel cased string into its components.

    :param src: Source string
    :return: A list containing the components
    """
    words = [[src[0]]]

    for c in src[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return ["".join(word) for word in words]


def handle_cancel(root: Tk, event: Event = None):
    root.destroy()


def register_bindings(root: Tk) -> Tk:
    root.bind("<Escape>", partial(handle_cancel, root), add=True)

    return root


class Widget(ABC):
    NOOP_SYMBOL: str
    resizable: Tuple[bool, bool] = (True, True)
    withdraw: bool = True

    @cached_property
    def window(self) -> Tk:
        window = Tk()
        window.resizable(*self.resizable)

        if self.withdraw:
            window.withdraw()

        window.wm_title(self.title)

        return window

    def _register_bindings(self, root: Tk):
        rt = register_bindings(root)
        return root

    def cancel(self):
        return handle_cancel(self.window)

    @property
    def title(self) -> str:
        """
        Window title
        """
        return " ".join(split_camel_case(self.__class__.__name__))

    @property
    def noop_symbol(self) -> str:
        """
        A symbol to use when in terminal mode
        :return:
        """
        assert (
            self.NOOP_SYMBOL is not None
        ), f"{self.__class__.__name__} does not define NOOP_SYMBOL"

        return self.NOOP_SYMBOL

    def gui(self):
        root = self.window
        style = ttk.Style(root)
        if os.fork != 0:
            # root.configure(bg=DEFAULT_BG_COLOR)
            # if DEFAULT_FONT_FAMILY and DEFAULT_FONT_SIZE:
            #     font.nametofont("TkDefaultFont").config(family=DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE)
            plugin = self.get_plugin(root, **self.plugin_params())
            root.mainloop()
        else:
            sys.stdout.write(self.noop_symbol)

    @abstractmethod
    def get_plugin(self, root: Tk, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def plugin_params(self) -> Mapping[str, Any]:
        raise NotImplementedError
