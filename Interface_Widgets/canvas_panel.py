# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from PIL import ImageTk


class CanvasPane(ttk.Frame):

    __slots__ = "interface", "image_pro", "canvas", "drawn", "current_image"

    def __init__(self, interface, *args, **kwargs):
        ttk.Frame.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.image_pro = interface.image_pro

        self.canvas = ttk.Label(self)
        self.canvas.pack(side='top', fill='both', expand=True)

        # Canvas drawn image
        self.drawn = None
        # The current image drawn to canvas
        self.current_image = None

    def on_resize(self, event: tk.Event) -> None:
        """Resizes the current drawn image on the screen to the window size."""
        self.current_image = self.image_pro.resize_image(self.winfo_width(), self.winfo_height())
        # self.canvas.itemconfig(self.drawn, image=self.current_image)
        self.canvas.configure(image=self.current_image)

    def create_image(self, loaded_image: ImageTk.PhotoImage) -> None:
        """Creates the first image and draws it to the canvas."""
        if self.drawn:
            self.set_current_drawn(loaded_image)
        else:
            # self.drawn = self.canvas.create_image(0, 0, image=loaded_image, anchor='nw')
            self.canvas.configure(image=loaded_image)
            self.bind("<Configure>", self.on_resize)
            self.current_image = loaded_image

    def set_current_drawn(self, loaded_image: ImageTk.PhotoImage) -> None:
        """Sets the image loaded image to the canvas."""
        # self.canvas.itemconfigure(self.drawn, image=loaded_image)
        self.canvas.configure(image=loaded_image)
        self.current_image = loaded_image

    def destroy_images(self) -> None:
        """Destroys all the images drawn to the canvas."""
        self.drawn = None
