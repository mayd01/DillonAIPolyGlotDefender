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

# Load good and bad files
good_files_dir = "/mnt/shared/good_files/"  # Path to good files
bad_files_dir = "/mnt/shared/bad_files/"  # Path to bad (polyglot) files
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
good_files = [os.path.join(good_files_dir, f) for f in os.listdir(good_files_dir)]
bad_files = [os.path.join(bad_files_dir, f) for f in os.listdir(bad_files_dir)]

# Extract byte sequences from files
good_sequences = np.array([extract_byte_sequence(f) for f in good_files])
bad_sequences = np.array([extract_byte_sequence(f) for f in bad_files])

# Labels: 1 for good, 0 for bad
good_labels = np.ones(len(good_sequences))
bad_labels = np.zeros(len(bad_sequences))

# Combine good and bad sequences and labels
X = np.concatenate([good_sequences, bad_sequences])
y = np.concatenate([good_labels, bad_labels])

# Shuffle data
indices = np.arange(len(X))
np.random.shuffle(indices)
X = X[indices]
y = y[indices]

# Reshape for LSTM (samples, timesteps, features)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Define LSTM model
model = Sequential([
    Masking(mask_value=0.0, input_shape=(4096, 1)),  # Ignore zero-padded areas
    LSTM(128, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Output: 1 (good), 0 (bad)
])

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
model.fit(X, y, epochs=10, batch_size=16, verbose=1)

# Save trained model
model.save("good_bad_polyglot_detector.h5")
print("Model saved successfully!")

