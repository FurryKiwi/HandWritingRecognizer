# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

import time
import os
import natsort
from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame
from CustomTkWidgets.tool_tips import ToolTip
from Backend_Scripts.utils_4_processor import dump_json, read_json


class OutputPane(ttk.Frame):
    _default_font = ("Arial", 14)
    _pady = 15
    _padx = 0
    _label_width = 8
    _entry_width = 15
    _filename = "Output.json"

    __slots__ = "interface", "config_pro", "image_pro", "btn_frame", "title_frame", "main_frame", "packed", \
                "title_page", "current_image_path", "entries", "vs_frames", "default_config", "master_config"

    def __init__(self, interface, *args, **kwargs):
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

        # The output master dict to be saved to json file after the save btn is pressed.
        self.master_dict = {}

        self.create_ui()

    def create_ui(self) -> None:
        # Title Frame widgets
        self.title_page = ttk.Label(self.title_frame, text="No Output for this page", anchor='center',
                                    font=self._default_font)
        self.title_page.pack(side='top', anchor='center', pady=5, padx=5)

        # Button Frame Widgets
        save_all_btn = ttk.Button(self.btn_frame, text="Save All", command=self.save_output)
        save_all_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(save_all_btn, self.interface, msg="Save All Output")

        reload_saved_btn = ttk.Button(self.btn_frame, text="Reload", command=self.reload_save_output)
        reload_saved_btn.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(reload_saved_btn, self.interface, msg="Reloads the last saved output.")

        update_excel = ttk.Button(self.btn_frame, text="Update Excel", command=self.update_excel)
        update_excel.pack(side='left', anchor='nw', padx=2, pady=2)
        ToolTip(update_excel, self.interface, msg="Updates the selected Excel spreadsheet.")

    def show_panel(self):
        """Draws the Panel to the screen."""
        if not self.packed:
            self.grid(column=1, row=1, sticky='nwse')
            self.packed = True

    def hide_panel(self):
        """Hides the Panel from the screen."""
        if self.packed:
            self.grid_forget()
            self.packed = False

    def reload_save_output(self):
        """Reloads a save json file output from a last scanned set of images."""
        if self.image_pro.orig_images_paths:
            try:
                filepath = tk.filedialog.askopenfilename(filetypes=[("Json Files", ".json")])
                if filepath != '':
                    self.master_dict = read_json(filepath)
                    if self.master_dict:
                        self.image_pro.set_output(self.master_dict)
                        self.create_pages(self.master_dict)
                        self.set_page(self.image_pro.current_image_path)
            except FileNotFoundError:
                tk.messagebox.showerror("No File", "Please select a file to open.", parent=self.interface)
        else:
            tk.messagebox.showerror("No Images", "Please load the images first,\n prior to reloading the output.",
                                    parent=self.interface)

    def update_excel(self):
        # TODO: Call the save_output function with the config path that is set for where to save the output.
        # TODO: Give a way for user to check what will be updated in the excel sheet. Use the tree view widget?
        pass

    def _generate_filename(self, filepath):
        filename = os.path.join(filepath, f"{time.strftime('%Y-%m-%d')}_{self._filename}")
        return filename

    def save_output(self) -> None:
        """Dump all the entries into a json file with the key being the filepath of each image."""
        if not self.entries:
            return None
        if tk.messagebox.askyesno("Save Output", "Are you sure all output is correct?", parent=self.interface):
            filepath = tk.filedialog.askdirectory(title="Select where you want to save the file:",
                                                  parent=self.interface)
            if filepath == "":
                raise Exception
            # Set the filepath and name of file
            new_filepath = self._generate_filename(filepath)
            self.master_dict = self._generate_master_output()
            try:
                dump_json(new_filepath, self.master_dict)
                tk.messagebox.showinfo("Success", "Output has been saved to file.", parent=self.interface)
            except Exception:
                tk.messagebox.showerror("Error", "Something went wrong and couldn't save the output.\n"
                                                 "Contact the developer.",
                                        parent=self.interface)

    def _generate_master_output(self):
        """Generates the output from all the entries in each image."""
        self.master_dict = {}
        sorted_keys = natsort.natsorted([f for f in self.entries.keys()])
        for key in sorted_keys:
            numbers = []
            for widgets in self.entries[key]:
                entry, _ = widgets
                numbers.append(int(entry.get()))
            self.master_dict.update({key: numbers})
        return self.master_dict

    def create_pages(self, output: dict) -> None:
        """Creates all the output entries for each page and stores in into memory."""
        self.destroy_widgets()
        self.vs_frames = {}
        self.entries = {}
        for key, values in output.items():
            vs_frame = VerticalScrolledFrame(self.main_frame)
            self.vs_frames.update({key: vs_frame})
            if values:
                entries = self.create_widgets(vs_frame.interior, values)
                self.entries.update({key: entries})
            else:
                self.entries.update({key: []})

    def destroy_widgets(self):
        """Destroys all vs_frames and all widgets inside said frame."""
        if self.vs_frames:
            print("Destroying Output Panel...")
            for widget in self.vs_frames.values():
                widget.destroy()
                del widget
        del self.vs_frames
        del self.entries

    def update_page(self, image_path, output: list) -> None:
        """Updates the current output panel page with the newly processed output."""
        self._destroy_entry_label(image_path)
        self.entries.pop(image_path)
        entries = self.create_widgets(self.vs_frame.interior, output)
        self.entries.update({image_path: entries})

    def _destroy_entry_label(self, image_path: str) -> None:
        for widgets in self.entries[image_path]:
            entry, label = widgets
            entry.destroy()
            label.destroy()

    def set_page(self, cur_img_path: str) -> None:
        """Pack the vs_frame for the currently drawn image in the canvas."""
        if self.vs_frame:
            self.vs_frame.pack_forget()
        if cur_img_path in list(self.vs_frames.keys()):
            if self.entries[cur_img_path]:
                title = cur_img_path.split("\\")[1]
                self.title_page.configure(text=title)
            else:
                self.title_page.configure(text="No Output for this page")
            self.vs_frame = self.vs_frames[cur_img_path]
            self.vs_frame.pack(side='top', fill='both', expand=True, pady=10, padx=10, anchor='center')
            self.current_image_path = cur_img_path
        else:
            self.title_page.configure(text="No Output for this page")

    def create_widgets(self, frame: tk.Frame | ttk.Frame, data: list) -> list:
        """The initial creation of the labels and entry's to be gridded onto the vs_frame."""
        w = []
        try:
            if not data:
                raise TypeError
            index = 1
            draw_index = len(data) - 1
            for value in data:
                label = ttk.Label(frame, font=self._default_font, text=draw_index, anchor='center',
                                  width=self._label_width)
                label.grid(column=0, row=index, pady=self._pady, padx=self._padx)

                new = ttk.Entry(frame, font=self._default_font, width=self._entry_width)
                new.grid(column=1, row=index, pady=self._pady, padx=self._padx)
                new.insert(0, str(value))

                ToolTip(new, self.interface, msg="Enter an Integer ONLY")
                new.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))

                index += 1
                draw_index -= 1

                w.append((new, label))
            return w
        except TypeError:
            print("Can't have an empty list or dict type.")

    def create_entry(self) -> ttk.Entry:
        """Creates a new ttk Entry and returns the object."""
        new = ttk.Entry(self.vs_frame.interior, font=self._default_font, width=self._entry_width)
        new.insert(0, "0")
        ToolTip(new, self.interface, msg="Enter an Integer ONLY")
        new.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))
        return new

    def create_label(self) -> ttk.Label:
        """Creates a new ttk Label and returns the object."""
        new = ttk.Label(self.vs_frame.interior, font=self._default_font, anchor='center', width=self._label_width)
        return new

    def pop_up_menu(self, event: tk.Event) -> None:
        """Creates a pop-up menu on the entries, to add and remove entries."""
        instance = event.widget

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Add Entry", command=lambda e=None: self.add_entry(instance))
        menu.add_command(label="Remove Entry", command=lambda e=None: self.remove_entry(instance))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_entry(self, instance: ttk.Entry) -> None:
        """Adds an entry below the currently selected entry."""
        # Reference for adding the new label and entry to the self.entries dict
        index_to_add = 0
        # Grab the selected entry's row
        grid_add = instance.grid_info()['row']
        # Create the new widgets to add
        new_entry = self.create_entry()
        new_label = self.create_label()
        for index, widgets in enumerate(self.entries[self.current_image_path]):
            # Grab the current entry row and label text
            entry, label = widgets
            row = entry.grid_info()['row']
            int_text = int(label.cget('text'))
            # If entry is the instance, change the label to add one and add the new label and entry below it by one
            if entry == instance:
                label.grid(column=0, row=grid_add, pady=self._pady, padx=self._padx)
                label.configure(text=str(int_text + 1))
                new_label.grid(column=0, row=grid_add + 1, pady=self._pady, padx=self._padx)
                new_label.configure(text=str(int_text))

                entry.grid(column=1, row=grid_add, pady=self._pady, padx=self._padx)
                new_entry.grid(column=1, row=grid_add + 1, pady=self._pady, padx=self._padx)

                index_to_add = index + 1
            # If below where the entry and label is being added, change the rest of the widgets down by one
            elif row > grid_add and entry != instance:
                label.grid(column=0, row=row + 1, pady=self._pady, padx=self._padx)
                entry.grid(column=1, row=row + 1, pady=self._pady, padx=self._padx)
            # If above where the entry and label is being added, change the above labels by adding one.
            elif row < grid_add and entry != instance:
                label.configure(text=str(int_text + 1))
        # Add the new label and entry to the dict.
        self.entries[self.current_image_path].insert(index_to_add, (new_entry, new_label))

    def remove_entry(self, instance: ttk.Entry) -> None:
        """Removes the selected entry from the output pane."""
        # Reference for where to remove the widgets
        index_to_remove = 0
        # Grab the current selected entry row
        grid_add = instance.grid_info()['row']
        for index, widgets in enumerate(self.entries[self.current_image_path]):
            entry, label = widgets
            # Grab each entry's row and label's text
            row = entry.grid_info()['row']
            int_text = int(label.cget('text'))
            # If the entry in dict == selected entry, unpack/un-grid both label and entry
            if entry == instance:
                index_to_remove = index
                label.grid_forget()
                instance.grid_forget()
            # If above the selected entry, change all labels to - 1. The ones below the selected entry don't need
            # to change.
            elif row < grid_add and entry != instance:
                label.configure(text=str(int_text - 1))
        # Remove the widgets from the dict
        self.entries[self.current_image_path].pop(index_to_remove)
