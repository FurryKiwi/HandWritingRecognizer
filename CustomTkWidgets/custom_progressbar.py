# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from Interface_Widgets.utils_4_tkinter import set_window


class CustomProgress(tk.Toplevel):
    _width, _height = 310, 100
    _title = "Processing Images..."
    _default_font = ("Arial", 14)

    __slots__ = "interface", "main_frame", "progress_bar", "time", "time_label"

    def __init__(self, interface, *args, **kwargs):
        tk.Toplevel.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.overrideredirect(True)
        set_window(self, self._width, self._height, self._title, parent=self.interface)

        self.main_frame = ttk.Frame(self, borderwidth=2, relief='raised')
        self.main_frame.pack(side='top', expand=True, fill='both')

        ttk.Label(self.main_frame, text="Please wait for processing to finish.", font=self._default_font,
                  anchor='center').pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=250,
                                            mode='indeterminate')
        self.progress_bar.pack(expand=True)

        self.progress_bar.start(20)

        self.time = 0

        self.time_label = ttk.Label(self.main_frame, text=f"{self.time}: seconds elapsed", font=self._default_font,
                                    anchor='center')
        self.time_label.pack(pady=5)

    def increase_time(self):
        self.time += 1
        self.time_label.configure(text=f"{self.time}: seconds elapsed")
