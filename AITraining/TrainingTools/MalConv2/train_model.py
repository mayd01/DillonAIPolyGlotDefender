import numpy as np
import os
from tensorflow import keras
from sklearn.model_selection import train_test_split
from malconv2 import MalConv2  # Replace with the MalConv2 model code from the previous messages

# Function to read bytes from a file and pad
def read_file_bytes(file_path, max_size=1000000):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))
    return np.frombuffer(file_bytes, dtype=np.uint8)

# Function to load and process the dataset
def load_dataset(directory, max_size=1000000):
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

# Load dataset
X, y = load_dataset("./data", max_size=1000000)

# Split dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the MalConv2 model (replace with your actual model creation function)
model = create_malconv2_model(input_shape=(1000000,))

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Save the model
model.save("./models/malconv2_model.h5")
