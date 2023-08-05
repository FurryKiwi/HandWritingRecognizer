# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

import cv2
import os
import json
import time
import functools
import numpy as np


def dump_json(filepath: str, data: dict | list) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()


def check_folder_and_create(filepath: str) -> None:
    if os.path.isdir(filepath):
        return
    else:
        os.makedirs(filepath)


def read_json(filename: str, data: dict | list = None) -> dict | list:
    """Read file data from the json file. Other-wise creates a new file."""
    try:
        with open(filename, 'r') as file:
            if os.path.getsize(filename) == 2 or os.path.getsize(filename) == 0:
                return create_json(filename, data)
            return json.load(file)
    except FileNotFoundError:
        return create_json(filename, data)


def create_json(filename: str, data: dict | list) -> dict | list:
    """Creates the json file if it doesn't exist."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()
        return data.copy()


def convert_to_grey(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def invert_image(img: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(img)


def draw_rectangle(x, y, w, h, image: np.ndarray) -> np.ndarray:
    cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
    return image


def draw_label(x, y, label, image: np.ndarray) -> np.ndarray:
    cv2.putText(image, label, (x - 80, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    return image


def get_single_digit_contours(image: np.ndarray) -> list:
    """Gets the contours of a single digit. Used for building datasets."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilate = cv2.dilate(image, kernel, iterations=2)
    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    return contours


def get_ones_contours(image: np.ndarray) -> list:
    """Gets the contours for digit one. Used when building datasets."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    dilate = cv2.dilate(image, kernel, iterations=1)
    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    return contours


def get_multi_digit_contours(image: np.ndarray) -> list:
    """Gets the contours of a multi digit image. Used for building test-sets."""
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=2)
    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    return contours


def write_image(filepath, image: np.ndarray) -> None:
    cv2.imwrite(filepath, image)


def read_image(image_path: str, mode: int = -1) -> np.ndarray:
    return cv2.imread(image_path, mode)


def sort_contours(cnts: list, method: str = "left-to-right"):
    """Sorts the contours from left_to_right in an image."""
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, bounding_boxes) = zip(*sorted(zip(cnts, bounding_boxes),
                                         key=lambda b: b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return cnts, bounding_boxes


def timefunc(func):
    """Timing decorator used to time how long it takes a function to execute."""

    @functools.wraps(func)
    def time_closure(*args, **kwargs):
        """time_wrapper's doc string"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - start
        print(f"Function: {func.__name__}, Time: {time_elapsed}")
        return result

    return time_closure
