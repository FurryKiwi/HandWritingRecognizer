# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog


class SelectableLabel(ttk.Label):

    __slots__ = "root", "config_pro", "class_name", "filepath"

    def __init__(self, frame, *args, **kwargs) -> None:
        ttk.Label.__init__(self, frame, *args, **kwargs)
        # .!settingspage I don't know a better way rn for getting the settingspage object
        self.root = frame.master.master.master.master.master.master.master
        self.config_pro = self.root.config_pro
        self.class_name = kwargs['class_']
        self.filepath = ""
        self.bind("<Button-1>", self.open_filepath)

    def open_filepath(self, event: tk.Event) -> None:
        filepath = tk.filedialog.askdirectory(parent=self.root)
        if filepath != "":
            self.filepath = filepath
            self.configure(text=self.filepath, foreground='white')
            self.config_pro.event_generate("<<FilePathSet>>")


class CustomTkEntry(tk.Entry):

    __slots__ = "class_name", "parent"

    def __init__(self, frame, class_name: str, *args, **kwargs) -> None:
        self.class_name = class_name
        self.parent = frame
        tk.Entry.__init__(self, frame, *args, **kwargs)
