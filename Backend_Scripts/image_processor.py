# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

from PIL import Image, ImageTk
import os
import natsort
import cv2
import numpy as np
from copy import deepcopy
from Backend_Scripts.utils_4_processor import read_image, convert_to_grey, sort_contours, \
    invert_image, draw_rectangle, draw_label, write_image, timefunc


class ImagePro(ttk.Frame):
    _extensions = [".png", ".jpg", ".jpeg"]

    __slots__ = "orig_images_paths", "_images", "original_images", "_digits_to_save", "output", "current_shown", \
                "current_index", "current_image_path", "interface", "config_pro", "model_pro"

    def __init__(self, interface, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, interface, *args, **kwargs)
        self.interface = interface
        self.config_pro = interface.config_pro
        self.model_pro = interface.model_pro

        # Stores all the filepaths to all the images before processing
        self.orig_images_paths = []
        # Stores all the images in a numpy arrays with the filepath as key, this dict will be overridden when the
        # preprocess method is called and the process method.
        self._images = {}
        # Stores the original images in a numpy array for use in the process function later on
        self.original_images = {}
        # Stores all the cropped roi images in a numpy array with the filepath key to be saved to a separate folder
        self._digits_to_save = {}
        # Stores all the output predictions of the digits in a dict
        self.output = {}
        # Current image drawn to canvas as an array so resizing is faster than going through the dict to grab it.
        self.current_shown = None
        # The current index in the orig_images_paths
        self.current_index = 0
        # Stores the current images path
        self.current_image_path = None

    def load_image_paths(self) -> None:
        """Loads all the images paths into a list in memory."""
        filepath = self.config_pro.get_path("Scanned Images Path")
        # default_filenames = self.config_pro.default_image_names
        # TODO: Do a check to see if the file in image_paths is == to the filenames in the default filenames, otherwise,
        #  rename all of them
        del self.orig_images_paths
        self.orig_images_paths = []
        image_paths = natsort.natsorted([f for f in os.listdir(filepath)])
        for file in image_paths:
            extension_check = os.path.splitext(file)[1]
            if extension_check in self._extensions:
                image_path = os.path.join(filepath, file)
                self.orig_images_paths.append(image_path)

    def get_image_paths(self) -> list:
        """Returns a copy of the image paths."""
        return deepcopy(self.orig_images_paths)

    def forward_image(self) -> np.ndarray:
        """Sets the current shown image forward by one in the loaded images."""
        self.current_index += 1
        if self.current_index >= len(self.orig_images_paths):
            self.current_index = 0
            self.current_image_path = self.orig_images_paths[self.current_index]
            self.current_shown = self._images[self.current_image_path]
            return self.current_shown
        else:
            self.current_image_path = self.orig_images_paths[self.current_index]
            self.current_shown = self._images[self.current_image_path]
            return self.current_shown

    def back_image(self) -> np.ndarray:
        """Sets the current shown image back by one in the loaded images."""
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.orig_images_paths) - 1
            self.current_image_path = self.orig_images_paths[self.current_index]
            self.current_shown = self._images[self.current_image_path]
            return self.current_shown
        else:
            self.current_image_path = self.orig_images_paths[self.current_index]
            self.current_shown = self._images[self.current_image_path]
            return self.current_shown

    def set_current_image(self) -> np.ndarray:
        """Sets the current image shown to the current index where the program has left off."""
        self.current_image_path = self.orig_images_paths[self.current_index]
        self.current_shown = self._images[self.current_image_path]
        return self.current_shown

    def get_output(self) -> tuple[dict, str] | tuple[None, None]:
        """Returns the output from the processed images if there is any along with the current image path."""
        if self.output:
            return self.output, self.current_image_path
        else:
            return None, None

    def get_current_output(self) -> tuple[dict, str] | tuple[None, None]:
        try:
            return self.output[self.current_image_path], self.current_image_path
        except KeyError:
            return None, None

    def get_current_img_path(self) -> str:
        """Helper function to get the current image path."""
        return self.current_image_path

    def get_image_size(self):
        """Helper function for getting the height of an image."""
        return self.current_shown.shape[0]

    def set_output(self, data: dict) -> None:
        """Sets the output data to the json file that has been read in from the Output Panel"""
        self.output = data
        del data

    def resize_image(self, width: int, height: int) -> ImageTk.PhotoImage:
        """Helper function to be called from the canvas when the window screen gets resized."""
        return self.convert_image_from_array(self.current_shown, width, height)

    @staticmethod
    def convert_image_from_array(image_array: np.ndarray, width: int, height: int) -> ImageTk.PhotoImage:
        """Converts the numpy array image to a Tk Photo Image, and resizes to the canvas size."""
        image = Image.fromarray(image_array)
        resized = image.resize((width, height), resample=Image.BICUBIC)
        del image
        return ImageTk.PhotoImage(resized)

    def load_orig_images_to_array(self) -> np.ndarray:
        """Loads the original images, convert to grayscale and save into arrays stores it in a dict."""
        del self._images
        del self.original_images
        self._images = {}
        for filepath in self.orig_images_paths:
            image = read_image(filepath, -1)
            image = convert_to_grey(image)
            self._images.update({filepath: image})
            del image
        self.original_images = deepcopy(self._images)
        self.current_index = 0
        self.current_shown = self._images[self.orig_images_paths[self.current_index]]
        self.current_image_path = self.orig_images_paths[self.current_index]
        return self.current_shown

    def preprocess_all(self) -> np.ndarray | None | bool:
        """Preprocesses the images with the going to be cropped area where the digits will be selected from."""
        if not self.orig_images_paths:
            return None
        del self._images
        self._images = deepcopy(self.original_images)
        config_data, check = self.config_pro.get_custom_config_all()
        if not check:
            if not tk.messagebox.askyesno("Warning", "Default values are about to be used. \n"
                                                     "Would you like to proceed?", parent=self.interface):
                return False
            for filepath, image in self._images.items():
                self._draw_crop_areas(config_data, image, filepath)
        else:
            for filepath, image in self._images.items():
                self._draw_crop_areas(config_data[filepath], image, filepath)
        return self.current_shown

    def preprocess_single(self) -> np.ndarray | None:
        if not self.orig_images_paths:
            return None
        image = deepcopy(self.original_images[self.current_image_path])
        config_data = self.config_pro.get_custom_config_by_key(self.current_image_path)
        self._draw_crop_areas(config_data, image, self.current_image_path)
        return self.current_shown

    def _draw_crop_areas(self, config: dict, image: np.ndarray, filepath) -> None:
        min_width = config["Crop Min Width"]
        max_width = config["Crop Max Width"]
        min_height = config["Crop Min Height"]
        max_height = config["Crop Max Height"]
        digit_min_width = config["Digit Min Width"]
        digit_min_height = config["Digit Min Height"]
        dilate_x = config["Dilation Width"]
        dilate_y = config["Dilation Height"]

        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_x, dilate_y))
        dilate = cv2.dilate(thresh, kernel, iterations=2)
        contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        index = 0
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # if w > digit_min_width and h > digit_min_height and x > min_width and x < max_width and y > min_height
            # and y < max_height:
            if w > digit_min_width and h > digit_min_height and min_width < x < max_width and \
                    min_height < y < max_height:
                draw_rectangle(min_width, min_height, (max_width - min_width), max_height, image)
                draw_rectangle(x, y, w, h, image)
                draw_label(x, y, str(index), image)
                self._images.update({filepath: image})
                index += 1
        else:
            # This grabs any image that doesn't have anything to crop on them
            self._images.update({filepath: image})
        self.current_shown = self._images[self.orig_images_paths[self.current_index]]
        self.current_image_path = self.orig_images_paths[self.current_index]
        del min_width, max_width, min_height, max_height, digit_min_width, digit_min_height, dilate_x, dilate_y
        del thresh, kernel, dilate, contours, index

    @timefunc
    def process_all(self, reprocess: bool) -> None:
        """Processes single and multi digits, calls the model predict function and sets the output of those
        predictions to the self.output. This function will check if an image has already been processed and skip
         those. If user wants to re-processes a single image, the process_single_image must be called."""
        for filepath, image in self.original_images.items():
            if reprocess:
                numbers = self._get_numbers(image, self.config_pro.get_custom_config_by_key(filepath))
                self.output.update({filepath: [values[0] for values in numbers]})
                del numbers
            else:
                if filepath not in list(self.output.keys()):
                    numbers = self._get_numbers(image, self.config_pro.get_custom_config_by_key(filepath))
                    self.output.update({filepath: [values[0] for values in numbers]})
                    del numbers

    def process_single(self, reprocess: bool):
        """Processes the current shown image and sets the output into the dict. This will not check if the image has
        been processed already, it will overwrite the current output for the current image."""
        if not reprocess:
            image = self.original_images[self.current_image_path]
            numbers = self._get_numbers(image, self.config_pro.get_custom_config_by_key(self.current_image_path))
            self.output.update({self.current_image_path: [values[0] for values in numbers]})
            del numbers
            del image

    def _get_numbers(self, image: np.ndarray, config) -> list:
        min_width = config["Crop Min Width"]
        max_width = config["Crop Max Width"]
        min_height = config["Crop Min Height"]
        max_height = config["Crop Max Height"]
        digit_min_width = config["Digit Min Width"]
        digit_min_height = config["Digit Min Height"]
        dilate_x = config["Dilation Width"]
        dilate_y = config["Dilation Height"]

        numbers = []
        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_x, dilate_y))
        dilate = cv2.dilate(thresh, kernel, iterations=2)
        contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > digit_min_width and h > digit_min_height and min_width < x < max_width and \
                    min_height < y < max_height:
                roi = image[y - 5:y + h + 5, x:x + w]
                new_image = invert_image(roi)
                numbers.append(self.process_multi_digits(new_image))
                del roi, new_image
        numbers.reverse()
        del min_width, max_width, min_height, max_height, digit_min_width, digit_min_height, dilate_x, dilate_y
        del thresh, kernel, dilate, contours
        return numbers

    def process_multi_digits(self, image: np.ndarray) -> list:
        """Crops and predicts all the digits and multi-digits in the contour, returns the numbers in a list of lists."""
        numbers = []
        prediction = []
        i = cv2.copyMakeBorder(src=image, top=10, bottom=10, left=10, right=10,
                               borderType=cv2.BORDER_CONSTANT)

        contours = cv2.findContours(i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = sort_contours(contours)[0]
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > 5 or h > 5:
                roi = i[y - 10:y + 10 + h, x - 10:x + 10 + w]
                roi = cv2.resize(roi, dsize=(56, 56), interpolation=cv2.INTER_CUBIC)
                image, img_shape = self.model_pro.reshape_digits(roi)
                p = self.model_pro.model.predict(image, verbose=0)
                prediction.append(np.argmax(p).astype(int))
        numbers.append(int(''.join(map(str, prediction))))
        del i, contours, roi, image, p, prediction
        return numbers
