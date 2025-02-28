import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

# Function to extract specific byte regions from files
def extract_features(file_path, regions=[(0, 256), (-256, None)]):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        features = []
        for start, end in regions:
            features.append(data[start:end] if end else data[start:])
        
        # Convert bytes to numpy array of uint8 (0-255) and normalize
        return np.concatenate([np.frombuffer(f, dtype=np.uint8) / 255.0 for f in features])
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Load dataset
def load_dataset(polyglot_dir, non_polyglot_dir):
    X, y = [], []
    
    for label, folder in enumerate([non_polyglot_dir, polyglot_dir]):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            features = extract_features(file_path)
            if features is not None:
                X.append(features)
                y.append(label)
    
    return np.array(X, dtype=object), np.array(y)

# Paths to datasets (Update these paths)
polyglot_dir = "path/to/polyglot_files"
non_polyglot_dir = "path/to/non_polyglot_files"

# Load data
X, y = load_dataset(polyglot_dir, non_polyglot_dir)

# Convert to consistent shape (padding/truncation)
max_length = max(len(x) for x in X)
X_padded = np.array([np.pad(x, (0, max_length - len(x)), mode='constant') for x in X])

# Reshape data for CNN input (samples, sequence_length, channels)
X_padded = X_padded.reshape(X_padded.shape[0], max_length, 1)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

# Define CNN model
model = keras.Sequential([
    keras.layers.Conv1D(filters=64, kernel_size=5, activation="relu", input_shape=(max_length, 1)),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=128, kernel_size=5, activation="relu"),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(filters=256, kernel_size=5, activation="relu"),
    keras.layers.GlobalAveragePooling1D(),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid")  # Binary classification
])

# Compile model
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Train model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Save model
model.save("polyglot_cnn_detector.h5")
