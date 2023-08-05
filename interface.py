# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>
try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog
from ttkthemes import ThemedTk

import Interface_Widgets.utils_4_tkinter as utils_tk
from Backend_Scripts.config_processor import ConfigPro
from Backend_Scripts.excel_processor import ExcelPro
from Backend_Scripts.image_processor import ImagePro
from Backend_Scripts.model_processor import ModelPro
from Backend_Scripts.style_processor import StylePro
from Interface_Widgets.settings_page import SettingsPage
from Interface_Widgets.canvas_panel import CanvasPane
from Interface_Widgets.output_panel import OutputPane
from Interface_Widgets.tool_panel import ToolPane
from Interface_Widgets.image_config_panel import ImageConfigPane


class Interface(ThemedTk):

    _width, _height = (1200, 600)
    _title = "Auto Excel Updater"
    _icon_path = r"Core/Data/journal.ico"

    __slots__ = "style", "config_pro", "excel_pro", "model_pro", "image_pro", "menubar", "settings_page", \
                "canvas_pane", "output_pane", "image_c_pane", "tool_pane"

    def __init__(self, *args, **kwargs) -> None:
        ThemedTk.__init__(self, *args, **kwargs)
        # Set theme first before configuring the styles of that theme
        self.set_theme("black")

        self.style = StylePro(self)
        self.config_pro = ConfigPro(self)
        self.excel_pro = ExcelPro(self)
        self.model_pro = ModelPro(self)
        self.image_pro = ImagePro(self)

        # UI Specific
        self.menubar = None
        self.settings_page = None
        self.canvas_pane = None
        self.output_pane = None
        self.image_c_pane = None
        self.tool_pane = None

        self.run()

    def create_file_menu(self) -> None:
        """Creates the file menu for the root window."""
        self.menubar = tk.Menu(self)
        menubar = self.menubar
        self.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        config_menu = tk.Menu(menubar, tearoff=0)

        # Create menus
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Settings", menu=config_menu)

        # Config menu
        config_menu.add_command(label="Settings Page", command=self.create_settings_page)

        # File menu
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._on_closing)

    def create_settings_page(self) -> None:
        """Creates the settings page."""
        if self.settings_page is None:
            self.settings_page = SettingsPage(self)
            self.settings_page.focus_set()
        else:
            try:
                self.settings_page.focus_set()
            except tk.TclError:
                self.settings_page = SettingsPage(self)

    def _on_closing(self) -> None:
        """Handles saving and quiting."""
        if tk.messagebox.askyesno("Quit!", "Do you want to quit?", parent=self):
            self.update_idletasks()
            self.destroy()

    def event_handling(self) -> None:
        self.bind('<Escape>', lambda event: self.state('normal'))
        self.bind('<F11>', lambda event: self.state('zoomed'))

    def run(self) -> None:
        """Main loop."""
        self.wm_iconbitmap(default=self._icon_path)
        self.create_file_menu()

        utils_tk.set_window(self, self._width, self._height, self._title, resize=True)

        self.minsize(width=1115, height=700)
        self.wm_state("zoomed")

        self.event_handling()

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        # Canvas pane
        self.canvas_pane = CanvasPane(self, relief='ridge')
        self.canvas_pane.grid(column=0, row=1, sticky='nwse')

        # Output pane
        self.output_pane = OutputPane(self, relief='ridge', borderwidth=1)

        # Image Config pane
        self.image_c_pane = ImageConfigPane(self, relief='ridge', borderwidth=1)

        # Tool pane
        self.tool_pane = ToolPane(self, relief='ridge', borderwidth=1)
        self.tool_pane.grid(column=0, row=0, sticky='nwse', columnspan=2)

        self.update_idletasks()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.wait_visibility(self)
        self.focus_set()


if __name__ == '__main__':
    r = Interface()
    r.mainloop()
