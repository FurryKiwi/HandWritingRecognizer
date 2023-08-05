# Copyright © 2023 FurryKiwi <normalusage2@gmail.com>

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras


class ModelPro:
    _path_to_model = os.path.join(os.getcwd(), "Core", "Model", "New_Optimizer_Model.h5")

    __slots__ = "interface", "config_pro", "model"

    def __init__(self, interface) -> None:
        self.interface = interface
        self.config_pro = interface.config_pro
        self.model = tf.keras.models.load_model(self._path_to_model, compile=False)

    @staticmethod
    def reshape_digits(train_dataset: np.ndarray, val_dataset: np.ndarray = None, image_size: int = 56) -> \
            tuple[np.ndarray, np.ndarray, tuple[int, int, int]] | tuple[np.ndarray, tuple[int, int, int]]:
        """Reshapes the image array based off of image input of channels first or last."""
        if keras.backend.image_data_format() == 'channels_first':
            in_shape = (1, image_size, image_size)
            train_dataset = train_dataset.reshape(-1, image_size, image_size, 1)  # NOQA
            if val_dataset is not None:
                val_dataset = val_dataset.reshape(-1, image_size, image_size, 1)  # NOQA
        else:
            in_shape = (image_size, image_size, 1)
            train_dataset = train_dataset.reshape(-1, image_size, image_size, 1)  # NOQA
            if val_dataset is not None:
                val_dataset = val_dataset.reshape(-1, image_size, image_size, 1)  # NOQA
        if val_dataset is not None:
            return train_dataset, val_dataset, in_shape
        else:
            return train_dataset, in_shape
