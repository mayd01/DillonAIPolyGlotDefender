import numpy as np
from tensorflow import keras
from malconv2 import MalConv2  # Replace with actual model code

# Load the trained model
model = keras.models.load_model("./models/malconv2_model.h5")

# Load test data (same preprocessing as during training)
X_test, y_test = load_dataset("./data/test_data", max_size=1000000)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
