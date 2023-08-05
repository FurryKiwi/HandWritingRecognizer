# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from CustomTkWidgets.custom_frames import SelectableFrames
from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame
from CustomTkWidgets.custom_widgets import SelectableLabel, CustomTkEntry
from CustomTkWidgets.tool_tips import ToolTip
import Interface_Widgets.utils_4_tkinter as utils_tk


class SettingsPage(tk.Toplevel):

    _title = "Settings"
    _headers = {"Paths Config": "Paths Config", "Image Config": "Image Tweaks"}

    __slots__ = "interface", "config_pro"

    def __init__(self, interface, *args, **kwargs) -> None:
        tk.Toplevel.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.config_pro = interface.config_pro

        _width, _height = (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2)
        self.minsize(width=self.winfo_screenwidth() // 2 - 185, height=self.winfo_screenheight() // 2)

        utils_tk.set_window(self, _width, _height, self._title, resize=True, parent=self.interface)

        custom_frames = CustomFrames(self, self._headers)
        custom_frames.pack(side='top', fill='both', expand=True, anchor='nw')


class CustomFrames(SelectableFrames):

    __slots__ = "interface", "config_pro", "headers_dict", "paths_page", "image_page"

    def __init__(self, settings_page: SettingsPage, headers: dict, **kwargs) -> None:
        SelectableFrames.__init__(self, settings_page, list(headers.values()), **kwargs)
        self.interface = settings_page.interface
        self.config_pro = settings_page.config_pro

        self.headers_dict = headers

        self.paths_page = None
        self.image_page = None

        self._setup_frames()
        self.change_frame(widget=self.initial_selected)

    def _setup_frames(self) -> None:
        for key, value in self.headers_dict.items():
            if key == "Paths Config":
                frame = self.get_new_frame(value)
                self.paths_page = PathsConfig(frame, self.interface, class_=value)
            elif key == "Image Config":
                frame = self.get_new_frame(value)
                self.image_page = ImageConfig(frame, self.interface, class_=value)

    def select_frame(self, class_name: str) -> None:
        """Sets the selected frame. This method is meant to be overridden by child class."""
        if self.options_frame is not None and self.options_frame.class_name == class_name:
            return

        if self.options_frame is not None:
            self.deselect_frame()

        if class_name == 'Paths Config':
            self.options_frame = self.paths_page
            self.options_frame.parent.pack(side='top', fill='both', expand=True, padx=4, pady=4)
        elif class_name == 'Image Tweaks':
            self.options_frame = self.image_page
            self.options_frame.parent.pack(side='top', fill='both', expand=True, padx=4, pady=4)

    def deselect_frame(self) -> None:
        """Unpacks the selected frame. This method is meant to be overridden by child class."""
        if self.options_frame is not None:
            self.options_frame.parent.pack_forget()


class PathsConfig:
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7

    __slots__ = "class_name", "parent", "interface", "config_pro", "main_frame", "labels"

    def __init__(self, parent_frame: ttk.Frame, interface, **kwargs) -> None:
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.interface = interface
        self.config_pro = interface.config_pro
        self.config_pro.bind("<<FilePathSet>>", self.set_config)

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.labels = []

        self.create_ui()

    def create_ui(self) -> None:

        labels_list = self.config_pro.paths_config

        vs_frame = VerticalScrolledFrame(self.main_frame)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        self.labels = self.create_labels_grid(vs_frame.interior, text=labels_list, font=self._font, pad_x=self._padx,
                                              pad_y=self._pady)

    def set_config(self, event: tk.Event) -> None:
        temp_dict = {}
        for i in self.labels:
            temp_dict.update({i.class_name: i.cget('text')})
        self.config_pro.set_paths_config(temp_dict)

    def create_labels_grid(self, frame: tk.Frame | ttk.Frame, text: dict, font: tuple[str, int], pad_y: int,
                           pad_x: int) -> list:
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        labels = []
        try:
            if not text:
                raise TypeError
            index = 0
            for key, value in text.items():
                ttk.Label(frame, text=f"{key}:", font=font).grid(column=0, row=index, pady=pad_y,
                                                                 padx=pad_x)
                if value == "~Click to Set Path!~":
                    new = SelectableLabel(frame, text=value, font=font, class_=key, foreground='yellow')
                    new.grid(column=1, row=index, pady=pad_y, padx=pad_x)
                else:
                    new = SelectableLabel(frame, text=value, font=font, class_=key,
                                          foreground='white')
                    new.grid(column=1, row=index, pady=pad_y, padx=pad_x)
                    ToolTip(new, self.interface, msg="Click to Set Path")
                index += 1
                labels.append(new)
            return labels
        except TypeError:
            print("Can't have an empty list or dict type.")


class ImageConfig:
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7

    __slots__ = "class_name", "parent", "interface", "config_pro", "image_pro", "title_frame", "main_frame", \
                "entries", "data"

    def __init__(self, parent_frame: ttk.Frame, interface, **kwargs) -> None:
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.interface = interface
        self.config_pro = interface.config_pro
        self.image_pro = interface.image_pro

        self.title_frame = ttk.Frame(self.parent, relief='sunken')
        self.title_frame.pack(side='top', fill='x', pady=4)

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.entries = []
        self.data = self.config_pro.get_image_config("")

        self.create_ui()

    def create_ui(self) -> None:
        # Title Frame
        set_config_btn = ttk.Button(self.title_frame, text="Set Config", command=self.set_config)
        set_config_btn.pack(side='left', anchor='nw', pady=2, padx=2)
        ToolTip(set_config_btn, self.interface, msg="Write Config to File")

        default_config_btn = ttk.Button(self.title_frame, text="Reset to Defaults", command=self.reset_defaults)
        default_config_btn.pack(side='left', anchor='nw', pady=2, padx=2)
        ToolTip(default_config_btn, self.interface, msg="Reset Config to Defaults")

        # Main Frame widgets
        vs_frame = VerticalScrolledFrame(self.main_frame)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        self.entries = self.create_labels_grid(vs_frame.interior, data=self.data)

    def reset_defaults(self) -> None:
        if tk.messagebox.askyesno("Reset Defaults", "Are you sure you want to reset to defaults?",
                                  parent=self.interface.settings_page):
            self.config_pro.set_default_image_config()
            self.data = self.config_pro.get_image_config("")
            values = [v for v in self.data.values()]
            for index, e in enumerate(self.entries):
                e.delete(0, 'end')
                e.insert(0, str(values[index]))

    def set_config(self) -> None:
        temp_dict = {}
        for i in self.entries:
            try:
                value = int(i.get())
                temp_dict.update({i.class_name: value})
            except Exception:
                tk.messagebox.showerror("Error", "Input has to be an integer\n"
                                                 "With no strings or characters or special characters.",
                                        parent=self.interface.settings_page)
                return None
        self.config_pro.set_image_config(temp_dict)

    def create_labels_grid(self, frame: tk.Frame | ttk.Frame, data: dict) -> list:
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        entries = []
        try:
            if not data:
                raise TypeError
            index = 0
            for key, value in data.items():
                ttk.Label(frame, text=f"{key}:", font=self._font).grid(column=0, row=index,
                                                                       pady=self._pady,
                                                                       padx=self._padx)
                new = CustomTkEntry(frame, font=self._font, class_name=key)
                new.grid(column=1, row=index, pady=self._pady, padx=self._padx)
                new.insert(0, str(value))
                if key == "Crop Max Height":
                    new.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))
                ToolTip(new, self.interface, msg="Enter an Integer ONLY")
                index += 1
                entries.append(new)
            return entries
        except TypeError:
            print("Can't have an empty list or dict type.")

    def pop_up_menu(self, event: tk.Event) -> None:
        """Creates a pop-up menu on the entries, to add and remove entries."""
        instance = event.widget

        menu = tk.Menu(self.interface.settings_page, tearoff=0)
        menu.add_command(label="Set Image Height", command=lambda e=None: self.set_image_height(instance))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def set_image_height(self, instance: ttk.Entry):
        try:
            image_height = self.image_pro.get_image_size()
            instance.delete(0, 'end')
            instance.insert(0, image_height)
        except AttributeError:
            tk.messagebox.showerror("Error", "Can't get the size of an unloaded image.\n"
                                             "Please load images.", parent=self.interface.settings_page)

