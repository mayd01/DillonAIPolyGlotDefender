import numpy as np
import os
from tensorflow import keras
from sklearn.model_selection import train_test_split
from malconv2 import MalConv2  # Replace with the MalConv2 model code from the previous messages

def read_file_bytes(file_path, max_size=1000000):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))
    return np.frombuffer(file_bytes, dtype=np.uint8)

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

X, y = load_dataset("./data", max_size=1000000)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = create_malconv2_model(input_shape=(1000000,))

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

model.save("./models/malconv2_model.h5")
