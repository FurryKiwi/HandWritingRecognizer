# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog


class StylePro(ttk.Style):
    _default_font_bold = ("Arial", 12, "bold")

    def __init__(self, root):
        ttk.Style.__init__(self, root)
        self._setup_styles()

    def _setup_styles(self):
        """Set custom styles here for widgets."""
        self.configure("TButton", anchor='center', focuscolor="black", focus=".", font=self._default_font_bold)
        self.configure("Red.TButton", anchor='center', focuscolor="black", focus=".", font=self._default_font_bold,
                       foreground="red")
