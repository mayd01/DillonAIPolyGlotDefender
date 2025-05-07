import numpy as np
from tensorflow import keras
from D22 import D22  # Replace with actual model code

model = keras.models.load_model("./models/D22_model.h5")

X_test, y_test = load_dataset("./data/test_data", max_size=1000000)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
