# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk

import os
from copy import deepcopy
from Backend_Scripts.utils_4_processor import read_json, dump_json, check_folder_and_create


class ConfigPro(ttk.Frame):
    # The config directory path
    _directory_of_configs = os.path.join(os.getcwd(), "Core", "Config")
    # The data output directory path
    _directory_of_data = os.path.join(os.getcwd(), "Core", "DataOut")
    # For the paths-config file
    _config_paths = "Config_Paths.json"
    _path_to_config = os.path.join(_directory_of_configs, _config_paths)
    # For the image settings config file
    _config_image = "Config_Image.json"
    _path_to_config_image = os.path.join(_directory_of_configs, _config_image)

    # For the renaming of the image files
    _sheet_names = "stock_lookup.json"
    _path_to_sheet_names = os.path.join(_directory_of_configs, _sheet_names)

    # TODO: Move all of this to a separate py file used to hardcode in default settings/configs.
    # Default Data for the configs
    _default_paths_config = {"Excel Path": "~Click to Set Path!~", "Scanned Images Path": "~Click to Set Path!~",
                             "Save Image Path": "~Click to Set Path!~"}
    _default_image_config = {"Crop Min Width": 590, "Crop Max Width": 1050,
                             "Crop Min Height": 175, "Crop Max Height": 9999,
                             "Digit Min Width": 15, "Digit Min Height": 20,
                             "Dilation Width": 19, "Dilation Height": 1}
    # These sheet names will be set from the Excel Component of the program
    _default_sheet_names = ["STOCK SHELF 1", "STOCK SHELF 2", "STOCK SHELF 3", "STOCK SHELF 4", "STOCK SHELF 5",
                            "STOCK SHELF 6", "STOCK SHELF 7", "STOCK SHELF 7(1)", "STOCK SHELF 8", "STOCK SHELF 9",
                            "STOCK SHELF 10", "STOCK SHELF 10(1)", "STOCK SHELF 11", "STOCK SHELF 12", "STOCK SHELF 13",
                            "STOCK SHELF 14", "STOCK SHELF 15", "STOCK SHELF 16", "STOCK SHELF 17", "STOCK SHELF 17(1)",
                            "STOCK SHELF 18", "STOCK SHELF 19", "STOCK SHELF 20", "STOCK SHELF 21", "STOCK SHELF 21(1)",
                            "STOCK SHELF 21(2)", "STOCK SHELF 22", "STOCK SHELF 22(1)", "STOCK SHELF 23",
                            "STOCK SHELF 24", "STOCK SHELF 24(1)", "STOCK SHELF 25", "STOCK SHELF 25(1)",
                            "STOCK SHELF 26", "STOCK SHELF A", "STOCK SHELF B", "STOCK SHELF C", "STOCK SHELF D",
                            "STOCK SHELF E", "STOCK SHELF F", "STOCK SHELF G", "STOCK SHELF H"
                            ]

    __slots__ = "interface", "paths_config", "default_image_config", "cur_image_config"

    def __init__(self, interface, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, interface, *args, **kwargs)
        self.interface = interface

        # Set up the config directory
        check_folder_and_create(self._directory_of_configs)
        # Set up the data_output directory
        check_folder_and_create(self._directory_of_data)
        # Read in the paths config
        self.paths_config = read_json(self._path_to_config, self._default_paths_config)
        # Read in the image config
        self.default_image_config = read_json(self._path_to_config_image, self._default_image_config)
        # Read in the default image names for the sheets
        # self.default_image_names = read_json(self._path_to_sheet_names, self._default_sheet_names)
        # Stores all the image configs in a dict from the image config panel for all the custom image settings
        self.cur_image_config = {}

    def set_paths_config(self, data: dict) -> None:
        """Sets the path's config."""
        dump_json(self._path_to_config, data)
        self.paths_config = data

    def get_path(self, key: str) -> str:
        """Returns the value from the given key."""
        return self.paths_config[key]

    def set_image_config(self, data: dict) -> None:
        """Sets the image config for the default values. Used for the settings page."""
        dump_json(self._path_to_config_image, data)
        self.default_image_config = data

    def get_image_config(self, key: str) -> int | dict:
        """Returns the value from the given key, otherwise returns the entire dict. Used for the settings page with the
        default settings."""
        if key == "":
            return deepcopy(self.default_image_config)
        else:
            return self.default_image_config[key]

    def set_default_image_config(self) -> None:
        """Resets the default image config values."""
        # TODO: Change the name of the Config_Image.json file to Default_Config_Image.json
        dump_json(self._path_to_config_image, self._default_image_config)
        self.default_image_config = self._default_image_config

    def set_custom_image_config(self, data: dict) -> None:
        """Sets the custom config settings for each image and writes to separate file."""
        self.cur_image_config = data

    def get_custom_config_by_key(self, image_path: str) -> dict:
        """Returns the custom config settings for the specified image."""
        return self.cur_image_config[image_path]

    def get_custom_config_all(self) -> tuple[dict, bool]:
        """Returns all the custom config settings for the images, unless they are equal to each other, then returns
        the default settings."""
        if not self._check_dicts_equal():
            return self.cur_image_config, True
        else:
            return self.default_image_config, False

    def _check_dicts_equal(self) -> bool:
        """Helper function to indicate if default values are being used for all images."""
        length = len(list(self.cur_image_config.keys()))
        values = [val for val in self.cur_image_config.values() if val == self.default_image_config]
        return True if length == len(values) else False
