from enum import Enum
from shutil import which
from subprocess import CalledProcessError, call, check_output
from tkinter import Button, Label, Tk, messagebox, Event, Frame, OptionMenu, StringVar
from typing import Iterable

from arf.peripherals.monitor.output import Output, Rotation, query_outputs, Reflection
from arf.widgets import handle_cancel


class Symbol(str, Enum):
    desktop = "\uf108"
    up_arrow = "\uf062"
    down_arrow = "\uf063"
    blanked = "\uf070"
    unblanked = "\uf06e"
    cloned = "\uf24d"
    not_cloned = "\uf096"
    primary = "\uf005"
    secondary = "\uf006"
    rotation_normal = "\uf151"
    rotation_left = "\uf191"
    rotation_right = "\uf152"
    rotation_inverted = "\uf150"
    reflection_normal = "\uf176"
    reflection_x = "\uf07e"
    reflection_y = "\uf07d"
    reflection_xy = "\uf047"
    toggle_on = "\uf205"
    toggle_off = "\uf204"
    apply = "\uf00c"
    cancel = "\uf00d"
    arandr = "\uf085"
    refresh = "\uf021"

    def __repr__(self):
        return self.value


WINDOW_CLOSE_TO_BOUNDARY_BUFFER = 20


class MonitorManager:

    # @property
    # def outputs(self) -> Iterable[Output]:
    #     return query_outputs()

    def __init__(self, root: Tk):
        self.root = root
        self.frame = None
        self.outputs = []
        self.hard_refresh_list()
        # style = {'bg': DEFAULT_BG_COLOR, 'fg': DEFAULT_FG_COLOR, 'relief': FLAT, 'padx': 1, 'pady': 1, 'anchor': 'w',
        #          'font': FONTAWESOME_FONT, 'bd': 0}
        style = {}

        self.info_label = Label(self.root, text="", **style)
        # self.info_label.config(bg=DEFAULT_BG_COLOR, font=DEFAULT_FONT)

        self.bottom_row = []

        self.apply_button = Button(self.root, text=Symbol.apply, **style)
        self.bottom_row.append(self.apply_button)

        self.refresh_button = Button(self.root, text=Symbol.refresh, **style)
        self.bottom_row.append(self.refresh_button)

        if which("arandr"):
            self.arandr_button = Button(self.root, text=Symbol.arandr, **style)
            self.bottom_row.append(self.arandr_button)
        else:
            self.arandr_button = None

        self.cancel_button = Button(self.root, text=Symbol.cancel, **style)
        self.bottom_row.append(self.cancel_button)

        self.info_label.grid(row=1, column=0, columnspan=len(self.bottom_row))
        self.grid_row(2, self.bottom_row)

        self.move_to_mouse()
        self.root.deiconify()

    def handle_cancel(self):
        return handle_cancel(self.root)

    def register_bindings(self):
        self.root.bind("<Return>", self.handle_apply)

        self.apply_button.bind("<Button-1>", self.handle_apply)
        self.set_info(self.apply_button, "Apply changes")

        self.refresh_button.bind("<Button-1>", self.hard_refresh_list)
        self.set_info(self.refresh_button, "Refresh list")

        if self.arandr_button:
            self.arandr_button.bind("<Button-1>", self.handle_arandr)
            self.set_info(self.arandr_button, "Launch aRandR")

        self.cancel_button.bind("<Button-1>", self.handle_cancel)
        self.set_info(self.cancel_button, "Cancel")

        for toggle_button in self.toggle_buttons:
            toggle_button.bind("<Button-1>", self.toggle_active)
            toggle_button.bind("<Button-4>", self.handle_up)
            toggle_button.bind("<Button-5>", self.handle_down)
            self.set_info(toggle_button, "Turn output on/off")

        for primary_button in self.primary_buttons:
            primary_button.bind("<Button-1>", self.set_primary)
            self.set_info(primary_button, "Set primary output")

        for blanked_button in self.blanked_buttons:
            blanked_button.bind("<Button-1>", self.toggle_blanked)
            self.set_info(blanked_button, "Show/hide output")

        for duplicate_button in self.duplicate_buttons:
            duplicate_button.bind("<Button-1>", self.toggle_duplicate)
            self.set_info(duplicate_button, "Duplicate another output")

        for rotate_button in self.rotate_buttons:
            rotate_button.bind("<Button-1>", self.cycle_rotation)
            self.set_info(rotate_button, "Rotate output")

        for reflect_button in self.reflect_buttons:
            reflect_button.bind("<Button-1>", self.cycle_reflection)
            self.set_info(reflect_button, "Reflect output")

        for brightness_slider in self.brightness_sliders:
            brightness_slider.bind("<ButtonRelease-1>", self.update_brightness)
            self.set_info(brightness_slider, "Adjust brightness")

        for up_button in self.up_buttons:
            up_button.bind("<Button-1>", self.handle_up)
            up_button.bind("<Button-4>", self.handle_up)
            up_button.bind("<Button-5>", self.handle_down)
            self.set_info(up_button, "Move up")

        for down_button in self.down_buttons:
            down_button.bind("<Button-1>", self.handle_down)
            down_button.bind("<Button-4>", self.handle_up)
            down_button.bind("<Button-5>", self.handle_down)
            self.set_info(down_button, "Move down")

    def grid_row(self, row, widgets):
        column = 0
        for w in widgets:
            w.grid(row=row, column=column)
            column += 1

    def move_to_mouse(self):
        root = self.root
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        x = root.winfo_pointerx() - width // 2
        y = root.winfo_pointery() - height // 2
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        if x + width > screen_width - WINDOW_CLOSE_TO_BOUNDARY_BUFFER:
            x = screen_width - WINDOW_CLOSE_TO_BOUNDARY_BUFFER - width
        elif x < WINDOW_CLOSE_TO_BOUNDARY_BUFFER:
            x = WINDOW_CLOSE_TO_BOUNDARY_BUFFER
        if y + height > screen_height - WINDOW_CLOSE_TO_BOUNDARY_BUFFER:
            y = screen_height - WINDOW_CLOSE_TO_BOUNDARY_BUFFER - height
        elif y < WINDOW_CLOSE_TO_BOUNDARY_BUFFER:
            y = WINDOW_CLOSE_TO_BOUNDARY_BUFFER

        root.geometry("+{}+{}".format(x, y))

    def set_info(self, widget, info):
        widget.bind(
            "<Enter>", lambda e: self.info_label.config(text=info)
        )  # , fg=DEFAULT_FG_COLOR))
        widget.bind("<Leave>", lambda e: self.info_label.config(text=""))

    def handle_apply(self, e=None):
        self.root.after_idle(self.do_handle_apply)

    def do_handle_apply(self):
        if not self.get_user_confirmation():
            return
        command = ["xrandr"]
        if not self.exists_primary():
            command += ["--noprimary"]

        partition = self.same_as_partition()
        prev_first_active = None
        for p in partition:
            first_active = None
            for output in p:
                command += ["--output", output.name]
                if output.active:
                    if first_active is None:
                        first_active = output
                    else:
                        command += ["--same-as", first_active.name]

                    if output.primary:
                        command += ["--primary"]
                    if prev_first_active is not None:
                        command += ["--right-of", prev_first_active.name]
                    if all([output.w, output.h, output.rate]):
                        command += ["--mode", "{}x{}".format(output.w, output.h)]
                        command += ["--rate", output.rate]
                    else:
                        command += ["--auto"]
                    command += ["--brightness", str(output.brightness)]
                    command += ["--rotate", output.rotation]
                    command += ["--reflect", output.reflection]
                else:
                    command += ["--off"]
            if first_active:
                prev_first_active = first_active
        self.root.after_idle(lambda: self.execute_xrandr_command(command))

    def execute_xrandr_command(self, command):
        try:
            check_output(command, universal_newlines=True)
        except CalledProcessError as err:
            self.info_label.config(
                text="xrandr returned nonzero exit status {}".format(err.returncode),
                fg="red",
            )

    def get_user_confirmation(self):
        result = "yes"
        if all(map(lambda o: o.blanked or not o.active, self.outputs)):
            result = messagebox.askquestion(
                "All blanked or off",
                "All ouputs are set to be turned off or blanked, continue?",
                icon="warning",
            )
        return result == "yes"

    def same_as_partition(self):
        partition = []
        for output in self.outputs:
            place = None
            for p in partition:
                if place is not None:
                    break
                for o in p:
                    if place is None and (
                        output.same_as == o.name or o.same_as == output.name
                    ):
                        place = p
                        break
            if place:
                place.append(output)
            else:
                partition.append([output])
        return partition

    def handle_arandr(self, e=None):
        call(["i3-msg", "-q", "exec", "arandr"])
        self.handle_cancel()

    def handle_up(self, e):
        row = e.widget.output.row
        if row > 0:
            self.swap_output_rows(row - 1, row)
        self.soft_refresh_list()

    def handle_down(self, e):
        row = e.widget.output.row
        n = len(self.outputs)
        if row + 1 < n:
            self.swap_output_rows(row, row + 1)
        self.soft_refresh_list()

    def swap_output_rows(self, row1, row2):
        outputs = self.outputs
        outputs[row1], outputs[row2] = outputs[row2], outputs[row1]
        outputs[row1].row = row1
        outputs[row2].row = row2
        for widget in self.frame.grid_slaves(row=row2):
            widget.output = outputs[row2]
        for widget in self.frame.grid_slaves(row=row1):
            widget.output = outputs[row1]

    def set_primary(self, e):
        output = e.widget.output
        output.primary = not output.primary
        for otherOutput in self.outputs:
            if otherOutput != output:
                otherOutput.primary = False
        self.soft_refresh_list()

    def exists_primary(self):
        for output in self.outputs:
            if output.primary:
                return True
        return False

    def toggle_active(self, e):
        output = e.widget.output
        output.active = not output.active
        if output.active:
            output.setPreferredMode()
        else:
            for otherOutput in self.outputs:
                if otherOutput.sameAs == output.name:
                    otherOutput.sameAs = None
        self.soft_refresh_list()

    def toggle_blanked(self, e):
        output = e.widget.output
        if output.blanked:
            output.blanked = False
            output.brightness = 1.0
        else:
            output.blanked = True
            output.brightness = 0.0
        self.soft_refresh_list()

    def update_brightness(self, e):
        output = e.widget.output
        output.brightness = 0.01 * e.widget.get()
        output.blanked = False
        if abs(output.brightness) < 1e-09:
            output.blanked = True
        self.soft_refresh_list()

    def cycle_rotation(self, e):
        output = e.widget.output
        if output.rotation == "normal":
            output.rotation = "right"
        elif output.rotation == "right":
            output.rotation = "inverted"
        elif output.rotation == "inverted":
            output.rotation = "left"
        else:
            output.rotation = "normal"
        self.soft_refresh_list()

    def rotation_symbol(self, rotation: Rotation) -> str:
        return {
            Rotation.NORMAL: Symbol.rotation_normal,
            Rotation.LEFT: Symbol.rotation_left,
            Rotation.RIGHT: Symbol.rotation_right,
            Rotation.INVERTED: Symbol.rotation_inverted,
        }[rotation]

    def cycle_reflection(self, event: Event):
        output = event.widget.output

        relfs = [*Reflection.__members__.values()]
        next_idx = (relfs.index(output.reflection) + 1) % len(relfs)
        output.reflection = relfs[next_idx]

        # if output.reflection == "normal":
        #     output.reflection = "x"
        # elif output.reflection == "x":
        #     output.reflection = "y"
        # elif output.reflection == "y":
        #     output.reflection = "xy"
        # else:
        #     output.reflection = "normal"
        self.soft_refresh_list()

    def reflection_symbol(self, reflection: Reflection):
        return {
            Reflection.NORMAL: Symbol.reflection_normal,
            Reflection.X: Symbol.reflection_x,
            Reflection.Y: Symbol.reflection_y,
            Reflection.XY: Symbol.reflection_xy,
        }[reflection]

    def toggle_duplicate(self, e):
        duplicateButton = e.widget
        optionMenu = duplicateButton.statusOptionMenu
        output = optionMenu.output
        if output.same_as is not None:
            output.same_as = None
            self.set_menu_to_output(optionMenu, output)
        else:
            self.set_menu_to_duplicate(optionMenu)
        self.soft_refresh_list()

    def get_duplicable_outputs_for(self, output):
        return [o for o in self.outputs if o != output and o.same_as is None]

    def soft_refresh_list(self, e=None):
        for widget in set().union(
            self.name_labels,
            self.primary_buttons,
            self.statusOptionMenus,
            self.blanked_buttons,
            self.duplicate_buttons,
            self.rotate_buttons,
            self.reflect_buttons,
            self.brightness_sliders,
            self.up_buttons,
            self.down_buttons,
        ):
            widget.config(
                fg=CONNECT_FG_COLOR if not widget.output.active else DISCONNECT_FG_COLOR
            )

        for widget in self.toggle_buttons:
            widget.config(
                text=Symbol.toggle_on if widget.output.active else Symbol.toggle_off
            )

        for widget in self.name_labels:
            widget.config(text=widget.output.name)

        for widget in self.primary_buttons:
            widget.config(
                text=Symbol.primary if widget.output.primary else Symbol.secondary
            )
            if not widget.output.primary:
                widget.config(fg=DEFAULT_FG_COLOR)

        for widget in self.statusOptionMenus:
            widget.config(text=widget.output.status())
            if widget.output.sameAs != None:
                self.set_menu_to_duplicate(widget)
                self.set_info(widget, "Select output to duplicate")
            else:
                self.set_menu_to_output(widget, widget.output)
                self.set_info(widget, "Select output mode")

        for widget in self.blanked_buttons:
            widget.config(
                text=Symbol.blanked if widget.output.blanked else Symbol.unblanked
            )

        for widget in self.duplicate_buttons:
            widget.config(
                text=Symbol.cloned if widget.output.sameAs else Symbol.not_cloned
            )

        for widget in self.rotate_buttons:
            widget.config(text=self.rotation_symbol(widget.output.rotation))

        for widget in self.reflect_buttons:
            widget.config(text=self.reflection_symbol(widget.output.reflection))

        for widget in self.brightness_sliders:
            widget.set(int(100 * widget.output.brightness))

    def hard_refresh_list(self, e=None):
        self.outputs = Output.realOutputs()
        self.root.after_idle(self.populateGrid)

    def populateGrid(self):
        oldFrame = self.frame
        self.frame = Frame(self.root)
        self.frame.configure(bg=DEFAULT_BG_COLOR)
        self.frame.grid(row=0, column=0, columnspan=len(self.bottom_row))
        self.toggle_buttons = []
        self.name_labels = []
        self.primary_buttons = []
        self.statusOptionMenus = []
        self.blanked_buttons = []
        self.duplicate_buttons = []
        self.rotate_buttons = []
        self.reflect_buttons = []
        self.brightness_sliders = []
        self.up_buttons = []
        self.down_buttons = []
        for row, output in enumerate(self.outputs):
            self.makeLabelRow(output, row)
        self.register_bindings()
        if oldFrame:
            oldFrame.destroy()

    def makeLabelRow(self, output, row):
        output.row = row
        style = {
            "bg": DEFAULT_BG_COLOR,
            "relief": FLAT,
            "padx": 1,
            "pady": 1,
            "anchor": "w",
        }
        widgets = []

        toggle_button = Button(self.frame, font=FONTAWESOME_FONT, **style)
        toggle_button.output = output
        self.toggle_buttons.append(toggle_button)
        if SHOW_ON_OFF:
            widgets.append(toggle_button)

        name_label = Label(self.frame, font=DEFAULT_FONT)
        name_label.output = output
        self.name_labels.append(name_label)
        if SHOW_NAMES:
            widgets.append(name_label)

        primaryButton = Button(self.frame, font=FONTAWESOME_FONT, **style)
        primaryButton.output = output
        self.primary_buttons.append(primaryButton)
        if not output.primary:
            primaryButton.config(fg=DEFAULT_FG_COLOR)
        if SHOW_PRIMARY:
            widgets.append(primaryButton)

        var = StringVar(self.frame)
        statusOptionMenu = OptionMenu(self.frame, var, None)
        statusOptionMenu.output = output
        statusOptionMenu.var = var
        statusOptionMenu.config(relief=FLAT)
        self.statusOptionMenus.append(statusOptionMenu)
        if SHOW_MODE or SHOW_DUPLICATE:
            widgets.append(statusOptionMenu)

        blankedButton = Button(self.frame, font=FONTAWESOME_FONT, **style)
        blankedButton.output = output
        self.blanked_buttons.append(blankedButton)
        if SHOW_BLANKED:
            widgets.append(blankedButton)

        duplicateButton = Button(self.frame, font=FONTAWESOME_FONT, **style)
        duplicateButton.statusOptionMenu = statusOptionMenu
        duplicateButton.output = output
        self.duplicate_buttons.append(duplicateButton)
        if SHOW_DUPLICATE:
            widgets.append(duplicateButton)

        rotateButton = Button(self.frame, font=FONTAWESOME_FONT, **style)
        rotateButton.output = output
        self.rotate_buttons.append(rotateButton)
        if SHOW_ROTATION:
            widgets.append(rotateButton)

        reflectButton = Button(self.frame, font=FONTAWESOME_FONT, **style)
        reflectButton.output = output
        self.reflect_buttons.append(reflectButton)
        if SHOW_REFLECTION:
            widgets.append(reflectButton)

        brightnessSlider = Scale(
            self.frame,
            orient="horizontal",
            from_=0,
            to=100,
            length=BRIGHTNESS_SLIDER_LENGTH,
            showvalue=SHOW_BRIGHTNESS_VALUE,
            sliderlength=BRIGHTNESS_SLIDER_HANDLE_LENGTH,
            width=BRIGHTNESS_SLIDER_WIDTH,
            font=FONTAWESOME_FONT,
        )
        brightnessSlider.output = output
        brightnessSlider.configure(bg=DEFAULT_BG_COLOR, fg="blue")
        self.brightness_sliders.append(brightnessSlider)
        if SHOW_BRIGHTNESS:
            widgets.append(brightnessSlider)

        upButton = Button(self.frame, text=UP_ARROW, font=FONTAWESOME_FONT, **style)
        upButton.output = output
        self.up_buttons.append(upButton)
        if SHOW_UP_DOWN:
            widgets.append(upButton)

        downButton = Button(self.frame, text=DOWN_ARROW, font=FONTAWESOME_FONT, **style)
        downButton.output = output
        self.down_buttons.append(downButton)
        if SHOW_UP_DOWN:
            widgets.append(downButton)

        for widget in widgets:
            widget.output = output
        self.grid_row(row, widgets)
        self.soft_refresh_list()

    def set_menu_to_output(self, optionMenu, output):
        menu = optionMenu["menu"]
        var = optionMenu.var
        modes = output.modes
        menu.delete(0, END)
        for i, mode in enumerate(modes):
            label = Output.modestr(mode)
            menu.add_command(
                label=label, command=setLabelAndOutputModeFunc(var, label, output, i)
            )
        if output.currentModeIndex != None:
            var.set(Output.modestr(modes[output.currentModeIndex]))
        elif output.preferredModeIndex != None:
            var.set(Output.modestr(modes[output.preferredModeIndex]))
        elif len(modes) > 0:
            var.set(Output.modestr(modes[0]))

    def set_menu_to_duplicate(self, optionMenu):
        menu = optionMenu["menu"]
        var = optionMenu.var
        output = optionMenu.output
        menu.delete(0, END)
        duplicables = self.get_duplicable_outputs_for(output)
        defaultIndex = 0
        for i, otherOutput in enumerate(duplicables):
            label = otherOutput.name
            menu.add_command(
                label=label, command=setLabelAndSameAsFunc(var, label, output)
            )
            if label == output.sameAs:
                defaultIndex = i
        if len(duplicables) > 0:
            var.set(menu.entrycget(defaultIndex, "label"))
            output.sameAs = menu.entrycget(defaultIndex, "label")
        else:
            var.set("None")

    def handleFocusOut(self, event):
        self.root.destroy()
