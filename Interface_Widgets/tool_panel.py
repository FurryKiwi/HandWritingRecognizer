# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from CustomTkWidgets.tool_tips import ToolTip
from CustomTkWidgets.custom_progressbar import CustomProgress
import threading


class ToolPane(ttk.Frame):

    __slots__ = "interface", "image_pro", "canvas", "output_pane", "image_c_pane", "thread", "output_shown", \
                "image_c_shown", "output_created", "progress_bar"

    def __init__(self, interface, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.image_pro = interface.image_pro
        self.canvas = interface.canvas_pane
        self.output_pane = interface.output_pane
        self.image_c_pane = interface.image_c_pane

        self.thread = None

        # Tracker for the output panel
        self.output_shown = False
        # Tracker for the image config panel
        self.image_c_shown = False
        # Check if the output has been created already
        self.output_created = False

        self.progress_bar = None

        self.create_ui()

    def create_ui(self) -> None:
        # Main Frames
        left_frame = ttk.Frame(self, relief='sunken')
        left_frame.pack(side='left', pady=10, padx=2, expand=True, fill='both')
        right_frame = ttk.Frame(self, relief='sunken')
        right_frame.pack(side='right', pady=10, padx=2, expand=True, fill='both')

        # Left frame widgets
        page_forward_btn = ttk.Button(left_frame, text=">", style="TButton", command=self.f_image)
        page_forward_btn.pack(side='right', anchor='ne', padx=2, pady=2)
        ToolTip(page_forward_btn, self.interface, msg="Page Forward")

        page_back_btn = ttk.Button(left_frame, text="<", style="TButton", command=self.b_image)
        page_back_btn.pack(side='right', anchor='ne', padx=2, pady=2)
        ToolTip(page_back_btn, self.interface, msg="Page Back")

        load_btn = ttk.Button(left_frame, text="Load", command=self.load_images)
        load_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(load_btn, self.interface, msg="Loads Original Images")

        pre_process_btn = ttk.Button(left_frame, text="Pre-Process All", command=self.pre_process_all)
        pre_process_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(pre_process_btn, self.interface, msg="Pre-Process All Images")

        process_btn = ttk.Button(left_frame, text="Process All", command=self.process_all_images)
        process_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(process_btn, self.interface, msg="Process All Images")

        process_single_btn = ttk.Button(left_frame, text="Process Page", command=self.process_single_image)
        process_single_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(process_single_btn, self.interface, msg="Process Current Image")

        pre_process_single_btn = ttk.Button(left_frame, text="Pre-Process Page", command=self.pre_process_single)
        pre_process_single_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(pre_process_single_btn, self.interface, msg="Pre-Process Current Image")

        # Right frame widgets
        show_output_btn = ttk.Button(right_frame, text="Show Output",
                                     command=lambda event=None: self.show_output_panel(show_output_btn,
                                                                                       image_config_btn))
        show_output_btn.pack(side='left', anchor='nw', pady=2, padx=2)
        ToolTip(show_output_btn, self.interface, msg="Shows the Output Panel")

        image_config_btn = ttk.Button(right_frame, text="Show Image Configs",
                                      command=lambda event=None: self.show_image_c_panel(show_output_btn,
                                                                                         image_config_btn))
        image_config_btn.pack(side='left', anchor='nw', pady=2, padx=2)
        ToolTip(image_config_btn, self.interface, msg="Shows the Image Config Panel")

    def show_output_panel(self, out_btn: ttk.Button, img_c_btn: ttk.Button) -> None:
        """Packs the output panel to the window."""
        if self.output_shown and not self.image_c_shown:
            self.output_pane.hide_panel()
            out_btn.configure(style="TButton")
            self.output_shown = False
        elif self.image_c_shown and not self.output_shown:
            self.image_c_pane.hide_panel()
            img_c_btn.configure(style="TButton")
            self.image_c_shown = False
            self.output_pane.show_panel()
            out_btn.configure(style="Red.TButton")
            self.output_shown = True
        else:
            self.output_pane.show_panel()
            out_btn.configure(style="Red.TButton")
            self.output_shown = True

    def show_image_c_panel(self, out_btn: ttk.Button, img_c_btn: ttk.Button) -> None:
        """Packs the image config panel to the window."""
        if self.image_c_shown and not self.output_shown:
            self.image_c_pane.hide_panel()
            img_c_btn.configure(style="TButton")
            self.image_c_shown = False
        elif self.output_shown and not self.image_c_shown:
            self.output_pane.hide_panel()
            out_btn.configure(style="TButton")
            self.output_shown = False
            self.image_c_pane.show_panel()
            img_c_btn.configure(style='Red.TButton')
            self.image_c_shown = True
        else:
            self.image_c_pane.show_panel()
            img_c_btn.configure(style='Red.TButton')
            self.image_c_shown = True

    def load_images(self) -> None:
        """Loads the original image paths and images into memory."""
        try:
            self.canvas.destroy_images()
            self.image_pro.load_image_paths()
            array = self.image_pro.load_orig_images_to_array()
            if array is None:
                raise Exception
            self.update_canvas()
            self.image_c_pane.create_pages(self.image_pro.get_image_paths(),
                                           self.image_pro.get_current_img_path())
            self.image_c_pane.set_page(self.image_pro.get_current_img_path())

        except Exception:
            self.canvas.destroy_images()
            tk.messagebox.showinfo("Error", "Could not load images from 'Scanned Images Path'\n"
                                            "Please set the correct path to the scanned images.", parent=self.interface)

    def pre_process_all(self) -> None:
        """Pre-processes original images to set where the crop area will be for grabbing the digits."""
        array = self.image_pro.preprocess_all()
        if array is None:
            tk.messagebox.showerror("Error", "No Images are loaded. \n"
                                             "Please Load Images first before trying to pre-process.",
                                    parent=self.interface)
            return None
        elif array is False:
            tk.messagebox.showinfo("Info", "Process has been terminated.", parent=self.interface)
            return None
        self.canvas.destroy_images()
        self.update_canvas()

    def pre_process_single(self) -> None:
        array = self.image_pro.preprocess_single()
        if array is None:
            tk.messagebox.showerror("Error", "No Images are loaded. \n"
                                             "Please Load Images first before trying to pre-process.",
                                    parent=self.interface)
            return None
        self.canvas.destroy_images()
        self.update_canvas()

    def process_all_images(self) -> None:
        """Processes all the images in the directory, and predicts the numbers and draws them to the output field."""
        # Do this check first here before a thread gets created.
        if not self.image_pro.original_images:
            tk.messagebox.showerror("Error", "No Images are loaded. \n"
                                             "Please Load Images first before trying to process.",
                                    parent=self.interface)
            return None
        if self.image_pro.output and self.output_created is True:
            if tk.messagebox.askyesno("Images Already Processed", "Are you sure you want to re-process image(s)?\n"
                                                                  "WARNING!\n"
                                                                  "Manually added entries will be lost!",
                                      parent=self.interface):
                self.create_thread(self.image_pro.process_all, creation=False, reprocess=True)
                self.output_created = True
            else:
                return None
        elif self.image_pro.output and self.output_created is False:
            if tk.messagebox.askyesno("Images Already Processed", "Are you sure you want to re-process image(s)?\n"
                                                                  "WARNING!\n"
                                                                  "Manually added entries will be lost!",
                                      parent=self.interface):
                self.create_thread(self.image_pro.process_all, creation=False, reprocess=True)
                self.output_created = True
            else:
                return None
        else:
            if tk.messagebox.askyesno("Process Images", "Are you sure all crop areas are set?\n"
                                                        "WARNING!\n"
                                                        "Manually added entries will be lost!",
                                      parent=self.interface):
                self.create_thread(self.image_pro.process_all, creation=True, reprocess=False)
                self.output_created = True
            else:
                return None

    def process_single_image(self) -> None:
        """Processes the currently selected image."""
        if not self.output_created:
            tk.messagebox.showinfo("Output Not Generated", "All Images must be processed at least once\n"
                                                           "prior to individual images being processed separately.",
                                   parent=self.interface)
            self.process_all_images()
            return None
        if self.image_pro.output and self.output_created is True:
            if tk.messagebox.askyesno("Image(s) Already Processed", "Are you sure you want to re-process image(s)?",
                                      parent=self.interface):
                self.create_thread(self.image_pro.process_single, creation=False, reprocess=False)

    def create_thread(self, func, creation: bool, reprocess: bool) -> None:
        """Creates a background thread for the processing of images."""
        del self.thread
        self.thread = threading.Thread(target=func, args=(reprocess,), daemon=True)
        self.thread.start()

        self.progress_bar = CustomProgress(self.interface)
        self.progress_bar.focus_set()
        self.progress_bar.grab_set()

        self.check_thread(creation, reprocess)

    def check_thread(self, creation: bool, reprocess: bool) -> None:
        """Checks if the _process_images is done."""
        if self.thread.is_alive():
            self.after(1000, lambda e=None: self.check_thread(creation, reprocess))
            self.progress_bar.increase_time()
        else:
            self.progress_bar.destroy()
            self.update_canvas()
            if creation is False and reprocess is False:
                output, current_image_path = self.image_pro.get_current_output()
                self.output_pane.update_page(current_image_path, output)
                self.output_pane.set_page(current_image_path)
            else:
                self.create_output_pane()
            self.update_idletasks()

    def update_canvas(self) -> None:
        """Updates the Canvas's image to be drawn."""
        array = self.image_pro.set_current_image()
        tk_photo = self.image_pro.convert_image_from_array(array, self.canvas.winfo_width(),
                                                           self.canvas.winfo_height())
        self.canvas.create_image(tk_photo)

    def create_output_pane(self) -> None:
        """Creates and sets the Output Panel."""
        output, current_image_path = self.image_pro.get_output()
        if current_image_path:
            self.output_pane.create_pages(output)
            self.output_pane.set_page(current_image_path)

    def f_image(self) -> None:
        """Sets the current image in the folder path forward by 1."""
        try:
            array = self.image_pro.forward_image()
            if array is None:
                raise IndexError
            self.update_canvas()

            self.image_c_pane.set_page(self.image_pro.get_current_img_path())

            _, current_image_path = self.image_pro.get_output()
            if current_image_path:
                self.output_pane.set_page(current_image_path)
        except IndexError:
            pass

    def b_image(self) -> None:
        """Sets the current image in the folder path back by 1."""
        try:
            array = self.image_pro.back_image()
            if array is None:
                raise IndexError
            self.update_canvas()

            self.image_c_pane.set_page(self.image_pro.get_current_img_path())

            _, current_image_path = self.image_pro.get_output()
            if current_image_path:
                self.output_pane.set_page(current_image_path)
        except IndexError:
            pass
