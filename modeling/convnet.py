import sys

import tensorflow as tf
import wandb
from tensorflow.keras.layers import (
    Flatten,
    MaxPooling3D,
    Dense,
    Dropout,
    Input,
    Conv3D,
)
from tensorflow.keras.models import Model, Sequential

sys.path.append(".")
from config import cfg
from data.dataset import Dataset


class ConvNet:
    """https://www.researchgate.net/publication/341116036_Two-Stage_Human_Activity_Recognition_Using_2D-ConvNet"""

    def build_model(input_shape, n_outputs, cfg):
        model = Sequential(
            [
                Input(shape=input_shape),
                Conv3D(8, kernel_size=(3, 3, 3), padding="same", activation="relu"),
                MaxPooling3D(pool_size=(2, 2, 1)),
                Conv3D(12, kernel_size=(3, 3, 3), padding="same", activation="relu"),
                MaxPooling3D(pool_size=(2, 2, 1)),
                Conv3D(24, kernel_size=(3, 3, 3), padding="same", activation="relu"),
                MaxPooling3D(pool_size=(2, 2, 1)),
                Flatten(),
                Dense(32, activation="relu"),
                Dense(32, activation="relu"),
                Dropout(0.5),
                Dense(n_outputs, activation="softmax"),
            ]
        )

        optimizer = getattr(tf.keras.optimizers, cfg.SOLVER.OPTIMIZER_NAME)
        optimizer = optimizer(lr=wandb.config.learning_rate, decay=1e-6)
        # Compile model
        model.compile(
            loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"]
        )

        return model
