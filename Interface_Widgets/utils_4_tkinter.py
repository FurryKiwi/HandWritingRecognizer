# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox


def set_window(root, w: int, h: int, title: str, parent=None, resize: bool = False, offset: tuple[int, int] = None,
               x_root=None, y_root=None) -> None:
    if parent:
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (w // 2)
        y = parent_y + (parent_height // 2) - (h // 2)
    elif x_root is not None and y_root is not None:
        x = (w // 2) + x_root
        y = (h // 2) + y_root
    else:
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
    root.title(title)
    if offset:
        root.geometry('%dx%d+%d+%d' % (w, h, x + offset[0], y + offset[1]))
    else:
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    if resize:
        root.resizable(1, 1)
    else:
        root.resizable(0, 0)
