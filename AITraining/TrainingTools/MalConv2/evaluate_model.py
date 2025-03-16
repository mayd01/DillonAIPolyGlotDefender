import numpy as np
from tensorflow import keras
from malconv2 import MalConv2, load_dataset  # Replace with actual model code

model = keras.models.load_model("./models/malconv2_model.h5")

X_test, y_test = load_dataset("/data/test_data", max_size=1000000)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
