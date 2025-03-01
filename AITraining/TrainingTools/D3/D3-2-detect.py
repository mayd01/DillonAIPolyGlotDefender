import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import sys

def extract_byte_sequence(file_path, seq_length=4096):
    """Reads a file and converts it into a normalized byte sequence."""
    with open(file_path, 'rb') as f:
        data = f.read(seq_length)
    
    byte_sequence = np.frombuffer(data, dtype=np.uint8)

    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized_sequence = scaler.fit_transform(byte_sequence.reshape(-1, 1)).flatten()
    
    if len(normalized_sequence) < seq_length:
        padded_seq = np.zeros(seq_length)
        padded_seq[:len(normalized_sequence)] = normalized_sequence
        return padded_seq
    else:
        return normalized_sequence[:seq_length]

# Load the trained model
model = load_model("bad_file_anomaly_detector_improved.h5")

def classify_file(file_path):
    """Classify a file as 'bad' or 'good'."""
    # Extract byte sequence from the file
    byte_sequence = extract_byte_sequence(file_path)
    
    # Reshape to match the model's expected input
    X = byte_sequence.reshape((1, len(byte_sequence), 1))
    
    # Predict using the model
    prediction = model.predict(X)
    print(f"Prediction: {prediction}")
    classification = (prediction > 0.5).astype(int)  # 0 = bad, 1 = good
    
    if classification == 0:
        print(f"The file '{file_path}' is classified as 'Bad'.")
    else:
        print(f"The file '{file_path}' is classified as 'Good'.")

# Test with a specific file
file_path_to_test = sys.argv[1]
classify_file(file_path_to_test)
