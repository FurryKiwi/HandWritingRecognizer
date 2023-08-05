# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog


class SelectableFrames(ttk.Frame):
    """Selectable ttk Frames that create a frame beside it when selected.

    Args: parent_frame: tk.Frame | ttk.Frame | tk.Tk,
        headers: list[str],
        background: str,
        active_background: str
    """

    _title_label_font = ("Arial", 20, "bold", "underline")
    __slots__ = "parent_frame", "headers", "background", "active_background", "options_frame", "selected_label", \
                "initial_selected", "main_frame", "first_frame"

    def __init__(self, parent_frame, headers: list, background: str = "#333333", active_background: str = "#007fff",
                 **kwargs) -> None:
        ttk.Frame.__init__(self, parent_frame, **kwargs)
        self.parent_frame = parent_frame
        self.headers = headers
        self.background = background
        self.active_background = active_background

        self.options_frame = None
        self.selected_label = None
        self.initial_selected = None

        self.main_frame = ttk.Frame(self, relief='ridge', borderwidth=1, padding=1)
        self.main_frame.pack(side='left', fill='y', expand=True, padx=4, pady=4, anchor='nw')

        self.first_frame = ttk.Frame(self, relief='ridge', borderwidth=1)
        self.first_frame.pack(side='left', fill='both', expand=True, padx=4, pady=4)

        self.custom_selectable_frames()

    def custom_selectable_frames(self) -> None:
        longest_string = max(self.headers, key=len)
        for i in range(len(self.headers)):
            new_label = ttk.Label(self.main_frame, class_=self.headers[i], width=len(longest_string) + 1,
                                  text=self.headers[i],
                                  background=self.background, foreground="white",
                                  font=("Arial", 20, "bold"), anchor='center')
            new_label.pack()
            new_label.bind("<Button-1>", lambda event: self.change_frame(event))
            if self.initial_selected is None:
                self.initial_selected = new_label

    def change_color(self, widget: ttk.Label) -> None:
        """Changes the background color of the label selected."""
        class_name = widget['class']
        if widget['background'] == self.active_background:
            widget['background'] = self.background
            self.deselect_frame()
        else:
            widget['background'] = self.active_background
            self.select_frame(class_name)

    def change_frame(self, event: tk.Event = None, widget: ttk.Label = None) -> None:
        """Changes the selected frame."""
        if event:
            widget = event.widget
        elif widget:
            widget = widget

        if self.selected_label is None:
            self.selected_label = widget
            self.change_color(self.selected_label)
        else:
            self.selected_label['background'] = self.background
            self.selected_label = widget
            self.change_color(self.selected_label)

    def get_new_frame(self, class_name: str) -> ttk.Frame:
        """Helper function to return a new ttk Frame and add a Title 'label' to the frame."""
        frame = ttk.Frame(self.first_frame, class_=class_name)
        ttk.Label(frame, text=f"{class_name} Page:", font=self._title_label_font,
                  width=200, anchor='center').pack(side='top')
        return frame

    def select_frame(self, class_name: str) -> None:
        """Sets the selected frame. This method is meant to be overridden by child class."""
        raise NotImplementedError("You have to override this method 'select_frame'.")

    def deselect_frame(self) -> None:
        """Unpacks the selected frame. This method is meant to be overridden by child class."""
        raise NotImplementedError("You have to override this method 'deselect_frame'.")
