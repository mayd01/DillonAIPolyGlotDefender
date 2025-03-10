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
good_files_dir = "/mnt/shared/downloads/"
good_files = [os.path.join(good_files_dir, f) for f in os.listdir(good_files_dir)]
good_sequences = np.array([extract_byte_sequence(f) for f in good_files])

# Reshape for LSTM (samples, timesteps, features)
X_train = good_sequences.reshape((len(good_sequences), good_sequences.shape[1], 1))



# Define LSTM model
model = Sequential([
    Masking(mask_value=0.0, input_shape=(4096, 1)),  # Ignore zero-padded areas
    LSTM(128, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Output: 1 (normal), 0 (anomaly)
])

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
model.fit(X_train, np.ones(len(X_train)), epochs=10, batch_size=16, verbose=1)


# Save trained model
model.save("polyglot_detector.h5")
print("Model saved successfully!")


# # Function to detect anomalies in a file
# def detect_polyglot(file_path):
#     """Predict if a file is an anomaly (polyglot) based on LSTM model."""
#     file_sequence = extract_byte_sequence(file_path).reshape(1, 4096, 1)
#     prediction = model.predict(file_sequence)[0][0]
    
#     if prediction < 0.5:  # Lower confidence = more likely polyglot
#         return "⚠️ Polyglot File Detected!"
#     else:
#         return "✅ File is Normal."

# # Test on a new file
# test_file = "path/to/test/file"
# print(detect_polyglot(test_file))
