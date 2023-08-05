from tkinter import ttk
import tkinter as tk


class VerticalScrolledFrame(ttk.Frame):
    __slots__ = "scroll_lock", "canvas", "interior", "interior_id"

    def __init__(self, parent, scroll_lock=False, *args, **kw) -> None:
        ttk.Frame.__init__(self, parent, *args, **kw)
        self.scroll_lock = scroll_lock

        # create a canvas object and a vertical scrollbar for scrolling it
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        v_scrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                yscrollcommand=v_scrollbar.set, background="#424242")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        v_scrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Enter>', self._bind_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_from_mousewheel)

    def _on_mousewheel(self, event):
        if not self.scroll_lock:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event: tk.Event) -> None:
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event: tk.Event) -> None:
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
