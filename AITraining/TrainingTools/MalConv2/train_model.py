import numpy as np
import os
from tensorflow import keras
from sklearn.model_selection import train_test_split
from malconv2 import MalConv2, create_model

def read_file_bytes(file_path, max_size=1000000):
    """Reads a file and returns its bytes as a numpy array, padded to max_size if necessary."""
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))  # Pad with null bytes
    return np.frombuffer(file_bytes, dtype=np.uint8)

def load_dataset(directory, max_size=1000000):
    """Loads a dataset from the given directory where files are divided into subfolders (e.g. non-polyglots, polyglots)."""
    files = []
    labels = []
    for label, sub_dir in enumerate(["non-polyglots", "polyglots"]):
        folder = os.path.join(directory, sub_dir)
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            byte_data = read_file_bytes(file_path, max_size)
            files.append(byte_data)
            labels.append(label)
    return np.array(files), np.array(labels)

# Load the dataset
X, y = load_dataset("./data", max_size=1000000)

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the MalConv2 model
malconv2_model = MalConv2()  # Use the class-based approach

# Train the model
malconv2_model.train(X_train, y_train, X_test, y_test, epochs=10, batch_size=32)

# Save the trained model
malconv2_model.save("./models/malconv2_model.h5")

# Optionally, evaluate the model
loss, accuracy = malconv2_model.evaluate(X_test, y_test)
print(f"Test loss: {loss}, Test accuracy: {accuracy}")
