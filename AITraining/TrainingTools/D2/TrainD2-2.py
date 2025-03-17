import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from tensorflow.keras import regularizers
import pickle

def load_preprocessed_data(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)

print("Loading preprocessed dataset...")
X_padded, y = load_preprocessed_data("preprocessed_data.pkl")
print("Dataset loaded.")

X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

max_length = X_padded.shape[1]

model = keras.Sequential([
    keras.layers.Conv1D(filters=64, kernel_size=5, activation="relu", input_shape=(max_length, 1)),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=128, kernel_size=5, activation="relu"),
    keras.layers.BatchNormalization(), 
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=256, kernel_size=5, activation="relu"),
    keras.layers.BatchNormalization(),  
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(0.01)),
    keras.layers.Dropout(0.5), 
    keras.layers.Dense(1, activation="sigmoid")
])

print("Model summary:")
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
print(model.summary())
checkpoint = keras.callbacks.ModelCheckpoint(
    "polyglot_cnn_detector_best.h5", save_best_only=True, monitor="val_accuracy", mode="max"
)

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
print("Training model...")
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test), callbacks=[checkpoint])
print("Training complete.")

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

model.save("polyglot_cnn_detector_final.h5")
