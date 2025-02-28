import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, RepeatVector, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import os

def extract_byte_sequence(file_path, seq_length=6098, chunk_size=1024):
    """Reads a file in chunks and converts it into a normalized byte sequence."""
    byte_sequence = []
    
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                byte_chunk = np.frombuffer(chunk, dtype=np.uint8)
                if byte_chunk.size == 0:
                    continue  # Skip empty chunks
                scaler = MinMaxScaler(feature_range=(0, 1))
                normalized_chunk = scaler.fit_transform(byte_chunk.reshape(-1, 1)).flatten()
                byte_sequence.extend(normalized_chunk)

                if len(byte_sequence) >= seq_length:
                    break
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return np.zeros(seq_length)  # Return zero array instead of None

    padded_seq = np.zeros(seq_length)
    padded_seq[:len(byte_sequence)] = byte_sequence[:seq_length]
    return padded_seq

# Directory where bad files are stored
bad_files_dir = "/mnt/shared/polyglots/"
bad_files = [os.path.join(bad_files_dir, f) for f in os.listdir(bad_files_dir) if os.path.isfile(os.path.join(bad_files_dir, f))]

if not bad_files:
    raise ValueError("No files found in the directory. Check if the directory exists and has valid files.")

# Extract byte sequences for each bad file
bad_sequences = [extract_byte_sequence(f) for f in bad_files]
bad_sequences = [seq for seq in bad_sequences if seq is not None and len(seq) > 0]  # Remove invalid sequences

if not bad_sequences:
    raise ValueError("No valid byte sequences extracted from files.")

bad_sequences = np.array(bad_sequences)

# Ensure the dataset shape is valid
if bad_sequences.ndim != 2:
    raise ValueError(f"Unexpected shape for dataset: {bad_sequences.shape}")

X = bad_sequences.reshape((bad_sequences.shape[0], bad_sequences.shape[1], 1))

# Define the Autoencoder model (Unsupervised Anomaly Detection)
input_seq = Input(shape=(X.shape[1], X.shape[2]))
encoded = LSTM(128, activation='relu', return_sequences=False)(input_seq)
encoded = RepeatVector(X.shape[1])(encoded)
decoded = LSTM(128, activation='relu', return_sequences=True)(encoded)
decoded = TimeDistributed(Dense(1))(decoded)

autoencoder = Model(inputs=input_seq, outputs=decoded)

# Compile the autoencoder
autoencoder.compile(optimizer='adam', loss='mean_squared_error')

# Early stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the autoencoder (only on bad files)
autoencoder.fit(X, X, epochs=30, batch_size=16, validation_split=0.2, callbacks=[early_stopping])

# Use the autoencoder to reconstruct the input data (Bad files)
reconstructed = autoencoder.predict(X)

# Calculate reconstruction error (Mean Squared Error) for each sample
reconstruction_error = np.mean(np.abs(X - reconstructed), axis=1)

# Set a threshold for anomaly detection
threshold = np.percentile(reconstruction_error, 95)  # Choose 95% of reconstruction error as threshold

# Detect anomalies based on reconstruction error exceeding the threshold
anomalies = reconstruction_error > threshold

# Print anomaly detection results
print(f"Threshold for anomalies: {threshold}")
print(f"Number of anomalies detected: {np.sum(anomalies)}")
print(f"Anomalies detected: {anomalies}")

# Optionally, save the model
autoencoder.save("anomaly_detector_autoencoder.h5")
print("Model saved successfully!")
