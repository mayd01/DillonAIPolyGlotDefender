import os
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib  # Import joblib to save/load the model

def extract_byte_features(file_path, max_bytes=4096):
    """Reads a file and extracts the first `max_bytes` as a feature vector."""
    with open(file_path, 'rb') as f:
        data = f.read(max_bytes)
    feature_vector = np.zeros(max_bytes, dtype=np.uint8)
    feature_vector[:len(data)] = np.frombuffer(data, dtype=np.uint8)
    return feature_vector

# Directory with "good" files for training
good_files_dir = "path/to/good/files"  # Ensure the correct path is set
if not os.path.exists(good_files_dir):
    raise FileNotFoundError(f"Directory {good_files_dir} not found!")

good_files = [os.path.join(good_files_dir, f) for f in os.listdir(good_files_dir) if os.path.isfile(os.path.join(good_files_dir, f))]
good_features = np.array([extract_byte_features(f) for f in good_files])

# Train the Isolation Forest model
iso_forest = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
iso_forest.fit(good_features)

# Save the trained model using joblib
model_filename = "isolation_forest_model.pkl"
joblib.dump(iso_forest, model_filename)
print(f"Model saved as {model_filename}")

def detect_polyglot(file_path, model):
    """Predict if a file is a polyglot/anomaly using the pre-trained model."""
    feature_vector = extract_byte_features(file_path).reshape(1, -1)
    prediction = model.predict(feature_vector)
    return "Polyglot File Detected!" if prediction[0] == -1 else "File is Normal."

# Load the model back for use
loaded_model = joblib.load(model_filename)
print(f"Model loaded from {model_filename}")

# Test file detection
test_file = "path/to/test/file"  # Ensure the correct test file path is set
print(detect_polyglot(test_file, loaded_model))
