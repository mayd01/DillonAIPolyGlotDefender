import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

# Function to extract byte regions from good files
def extract_features(file_path, regions=[(0, 256), (-256, None)]):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        features = []
        for start, end in regions:
            features.append(data[start:end] if end else data[start:])
        
        # Convert bytes to numpy array (0-255) and normalize
        return np.concatenate([np.frombuffer(f, dtype=np.uint8) / 255.0 for f in features])
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Load dataset of good files
def load_good_files(good_dir):
    X = []
    
    for file in os.listdir(good_dir):
        file_path = os.path.join(good_dir, file)
        features = extract_features(file_path)
        if features is not None:
            X.append(features)
    
    return np.array(X, dtype=object)

# Path to good files dataset (update this)
good_dir = "path/to/good_files"

# Load data
X = load_good_files(good_dir)

# Convert to consistent shape (padding/truncation)
max_length = max(len(x) for x in X)
X_padded = np.array([np.pad(x, (0, max_length - len(x)), mode='constant') for x in X])

# Reshape data for CNN input (samples, sequence_length, channels)
X_padded = X_padded.reshape(X_padded.shape[0], max_length, 1)

# Split into training and validation sets
X_train, X_test = train_test_split(X_padded, test_size=0.2, random_state=42)

# Define Autoencoder
input_shape = (max_length, 1)
encoder = keras.Sequential([
    keras.layers.Input(shape=input_shape),
    keras.layers.Conv1D(64, kernel_size=5, activation="relu", padding="same"),
    keras.layers.MaxPooling1D(pool_size=2),
    keras.layers.Conv1D(32, kernel_size=5, activation="relu", padding="same"),
    keras.layers.MaxPooling1D(pool_size=2)
])

decoder = keras.Sequential([
    keras.layers.Conv1D(32, kernel_size=5, activation="relu", padding="same"),
    keras.layers.UpSampling1D(size=2),
    keras.layers.Conv1D(64, kernel_size=5, activation="relu", padding="same"),
    keras.layers.UpSampling1D(size=2),
    keras.layers.Conv1D(1, kernel_size=5, activation="sigmoid", padding="same")  # Reconstruct original input
])

autoencoder = keras.Sequential([encoder, decoder])

# Compile model
autoencoder.compile(optimizer="adam", loss="mse")

# Train model
autoencoder.fit(X_train, X_train, epochs=10, batch_size=32, validation_data=(X_test, X_test))

# Save model
autoencoder.save("good_files_autoencoder.h5")

# Function to detect anomalies
def detect_anomaly(file_path, threshold=0.01):
    features = extract_features(file_path)
    if features is None:
        return None

    features_padded = np.pad(features, (0, max_length - len(features)), mode='constant')
    features_padded = features_padded.reshape(1, max_length, 1)
    
    reconstructed = autoencoder.predict(features_padded)
    error = np.mean(np.abs(features_padded - reconstructed))
    
    return "Anomalous (Potential Polyglot)" if error > threshold else "Normal (Good File)"

# Test anomaly detection
test_file = "path/to/test_file"
result = detect_anomaly(test_file)
print(f"File {test_file} is classified as: {result}")
