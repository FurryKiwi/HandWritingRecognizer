# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from CustomTkWidgets.tool_tips import ToolTip
from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame
from CustomTkWidgets.custom_widgets import CustomTkEntry


class ImageConfigPane(ttk.Frame):
    _default_font = ("Arial", 14)
    _pady = 15
    _padx = 0
    _label_width = 15
    _entry_width = 15

    __slots__ = "interface", "config_pro", "image_pro", "btn_frame", "title_frame", "main_frame", "packed", \
                "title_page", "current_image_path", "entries", "vs_frames", "default_config", "master_config"

    def __init__(self, interface, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.config_pro = interface.config_pro
        self.image_pro = interface.image_pro

        # The top btn frame
        self.btn_frame = ttk.Frame(self, relief='sunken')
        self.btn_frame.pack(side='top', padx=2, pady=2, fill='x', anchor='nw')

        # The top title frame
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(side='top', padx=2, pady=2, fill='x', anchor='nw')

        # The main frame for the scroll bar frame
        self.main_frame = ttk.Frame(self, relief='sunken')
        self.main_frame.pack(side='top', pady=2, padx=2, expand=True, fill='both', anchor='nw')

        self.packed = False

        # The current vs_frame to be shown per page.
        self.vs_frame = None

        # The current title label to be shown per page.
        self.title_page = None

        # Stores the current image path, so I can access which vs_frames I need to edit
        self.current_image_path = None

        # Stores all the entries for all the output, key being the filepath for the sheet
        self.entries = {}

        # Stores all the vs_frames for each page, key being the filepath for the sheet
        self.vs_frames = {}

        # Stores a copy of the config dict
        self.default_config = self.config_pro.get_image_config("")

        # Stores the current settings for all the images
        self.master_config = {}

        self.create_ui()

    def create_ui(self) -> None:
        # Title Frame Widget.
        self.title_page = ttk.Label(self.title_frame, text="No Images are loaded.", anchor='center',
                                    font=self._default_font)
        self.title_page.pack(side='top', anchor='center', pady=5, padx=5)

        # Button Frame Widgets
        set_config_btn = ttk.Button(self.btn_frame, text="Set Config", command=self.set_config)
        set_config_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(set_config_btn, self.interface, msg="Set Config for the current Image.")

        reset_config_btn = ttk.Button(self.btn_frame, text="Reset Config", command=self.reset_config)
        reset_config_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(reset_config_btn, self.interface, msg="Set Current Image Config to defaults.")

        reset_config_all_btn = ttk.Button(self.btn_frame, text="Reset All", command=self.reset_all_configs)
        reset_config_all_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(reset_config_all_btn, self.interface, msg="Set All Image(s) Configs to defaults.")

    def show_panel(self) -> None:
        """Draws the Panel to the screen."""
        if not self.packed:
            self.grid(column=1, row=1, sticky='nwse')
            self.packed = True

    def hide_panel(self) -> None:
        """Hides the Panel from the screen."""
        if self.packed:
            self.grid_forget()
            self.packed = False

    def set_config(self) -> None:
        """Sets the config for the current image and pass the image path and dict to the config pro."""
        if not self.current_image_path:
            return None
        self._update_all_configs()
        self.config_pro.set_custom_image_config(self.master_config)

    def _update_all_configs(self) -> None:
        """Updates the master config for all the entries and key being the file path to each image."""
        for key in self.entries.keys():
            temp_dict = {}
            for entry in self.entries[key]:
                temp_dict.update({entry.class_name: int(entry.get())})
            self.master_config.update({key: temp_dict})

    def reset_config(self) -> None:
        """Resets the config to default values that have been set in the settings page."""
        if not self.current_image_path:
            return None

        data = self.config_pro.get_image_config('')
        values = list(data.values())

        if tk.messagebox.askyesno("Current Image?", "Do you want to reset the config parameters\n"
                                                    "back to default settings\n"
                                                    "for the current image?", parent=self.interface):
            for index, entry in enumerate(self.entries[self.current_image_path]):
                entry.delete(0, 'end')
                entry.insert(0, values[index])
            self.set_config()
        del data
        del values

    def reset_all_configs(self):
        """Resets all the configs for all the images from the values set in the settings page."""
        if not self.current_image_path:
            return None

        data = self.config_pro.get_image_config('')
        values = list(data.values())

        if tk.messagebox.askyesno("All Images?", "Do you want to reset the config parameters\n"
                                                 "back to default settings\n"
                                                 "for all of the saved images?", parent=self.interface):
            for key in self.entries.keys():
                for index, entry in enumerate(self.entries[key]):
                    entry.delete(0, 'end')
                    entry.insert(0, values[index])
            self.set_config()
        del data
        del values

    def set_page(self, cur_img_path: str) -> None:
        """Pack the vs_frame for the currently drawn image and unpack the last one."""
        if self.vs_frame:
            self.vs_frame.pack_forget()
        title = cur_img_path.split("\\")[1]
        self.title_page.configure(text=title)
        self.vs_frame = self.vs_frames[cur_img_path]
        self.vs_frame.pack(side='top', fill='both', expand=True, pady=10, padx=10, anchor='center')
        self.current_image_path = cur_img_path

    def create_pages(self, image_paths: list, cur_img_path: str) -> None:
        """Creates all the widgets and stores them in dicts."""
        self.destroy_widgets()
        self.vs_frames = {}
        self.entries = {}
        for key in image_paths:
            vs_frame = VerticalScrolledFrame(self.main_frame)
            self.vs_frames.update({key: vs_frame})

            entries = self.create_widgets(vs_frame.interior, self.default_config)
            self.entries.update({key: entries})
        self.current_image_path = cur_img_path
        self.set_config()

    def destroy_widgets(self):
        """Destroys the vs_frames."""
        if self.vs_frames:
            for f in self.vs_frames.values():
                f.destroy()
                del f
        del self.vs_frames
        del self.entries

    def create_widgets(self, frame: tk.Frame | ttk.Frame, data: dict) -> list:
        """Initial creation of labels and entry's to be gridded onto the vs_frame."""
        w = []
        try:
            if not data:
                raise TypeError
            index = 0
            for key, value in data.items():
                ttk.Label(frame, text=f"{key}:", font=self._default_font, width=self._label_width).grid(column=0,
                                                                                                        row=index,
                                                                                                        pady=self._pady,
                                                                                                        padx=self._padx)
                new = CustomTkEntry(frame, font=self._default_font, class_name=key, width=self._entry_width)
                new.grid(column=1, row=index, pady=self._pady, padx=self._padx)
                new.insert(0, str(value))
                if key == "Crop Max Height":
                    new.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))
                    ToolTip(new, self.interface, msg="Enter an Integer ONLY\n Right-Click to add Image Height")
                else:
                    ToolTip(new, self.interface, msg="Enter an Integer ONLY")
                index += 1
                w.append(new)
            return w
        except TypeError:
            print("Can't have an empty list or dict type.")

    def pop_up_menu(self, event: tk.Event) -> None:
        """Creates a pop-up menu on the entries, to add and remove entries."""
        instance = event.widget

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Set Image Height", command=lambda e=None: self.set_image_height(instance))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def set_image_height(self, instance: ttk.Entry):
        """Sets the current image's height."""
        try:
            image_height = self.image_pro.get_image_size()
            instance.delete(0, 'end')
            instance.insert(0, image_height)
        except AttributeError:
            tk.messagebox.showerror("Error", "Can't get the size of an unloaded image.\n"
                                             "Please load images.", parent=self.interface)
