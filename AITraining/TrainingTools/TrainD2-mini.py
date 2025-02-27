import os
import numpy as np
from sklearn.ensemble import IsolationForest

# Function to extract byte features from files
def extract_byte_features(file_path, max_bytes=4096):
    """Reads a file and extracts the first `max_bytes` as a feature vector."""
    with open(file_path, 'rb') as f:
        data = f.read(max_bytes)
    # Pad or truncate to a fixed size
    feature_vector = np.zeros(max_bytes, dtype=np.uint8)
    feature_vector[:len(data)] = np.frombuffer(data, dtype=np.uint8)
    return feature_vector

# Load training data (good files)
good_files_dir = "path/to/good/files"
good_files = [os.path.join(good_files_dir, f) for f in os.listdir(good_files_dir)]
good_features = np.array([extract_byte_features(f) for f in good_files])

# Train Isolation Forest
iso_forest = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
iso_forest.fit(good_features)

# Function to predict new files
def detect_polyglot(file_path):
    """Predict if a file is a polyglot/anomaly."""
    feature_vector = extract_byte_features(file_path).reshape(1, -1)
    prediction = iso_forest.predict(feature_vector)  # -1 = anomaly, 1 = normal
    return "Polyglot File Detected!" if prediction[0] == -1 else "File is Normal."

# Test on a new file
test_file = "path/to/test/file"
print(detect_polyglot(test_file))
