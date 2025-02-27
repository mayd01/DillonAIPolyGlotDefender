import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Masking
from sklearn.preprocessing import MinMaxScaler

# Function to convert file bytes into a normalized sequence
def extract_byte_sequence(file_path, seq_length=4096):
    """Reads a file and converts it into a normalized byte sequence."""
    with open(file_path, 'rb') as f:
        data = f.read(seq_length)
    
    # Convert to numpy array (bytes → integers)
    byte_sequence = np.frombuffer(data, dtype=np.uint8)

    # Normalize to range [0, 1]
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized_sequence = scaler.fit_transform(byte_sequence.reshape(-1, 1)).flatten()
    
    # Pad or truncate to fixed sequence length
    if len(normalized_sequence) < seq_length:
        padded_seq = np.zeros(seq_length)
        padded_seq[:len(normalized_sequence)] = normalized_sequence
        return padded_seq
    else:
        return normalized_sequence[:seq_length]

# Load good files
good_files_dir = "path/to/good/files"
good_files = [os.path.join(good_files_dir, f) for f in os.listdir(good_files_dir)]
good_sequences = np.array([extract_byte_sequence(f) for f in good_files])

# Reshape for LSTM (samples, timesteps, features)
X_train = good_sequences.reshape((len(good_sequences), good_sequences.shape[1], 1))
