import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed
from sklearn.preprocessing import MinMaxScaler
import os
import sys

def extract_byte_sequence(file_path, seq_length=6098, chunk_size=1024):
    """Reads a file in chunks and converts it into a normalized byte sequence."""
    byte_sequence = []
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            # Convert the chunk into a normalized byte sequence
            byte_chunk = np.frombuffer(chunk, dtype=np.uint8)
            scaler = MinMaxScaler(feature_range=(0, 1))
            normalized_chunk = scaler.fit_transform(byte_chunk.reshape(-1, 1)).flatten()
            byte_sequence.extend(normalized_chunk)
            
            # If we have reached or exceeded the desired sequence length, stop reading
            if len(byte_sequence) >= seq_length:
                break
    
    # If the sequence is shorter than the desired length, pad with zeros
    if len(byte_sequence) < seq_length:
        padded_seq = np.zeros(seq_length)
        padded_seq[:len(byte_sequence)] = byte_sequence
        return padded_seq
    else:
        return byte_sequence[:seq_length]

def run_anomaly_detection(file_path, model_path='anomaly_detector_autoencoder.h5', seq_length=6098, threshold_percentile=95):
    """Runs anomaly detection on the provided file using a trained autoencoder model."""
    # Extract byte sequence from the file
    file_sequence = extract_byte_sequence(file_path, seq_length=seq_length)
    
    # Reshape input data to (1, seq_length, 1) for LSTM
    file_sequence_reshaped = file_sequence.reshape((1, seq_length, 1))
    
    # Load the trained autoencoder model
    autoencoder = load_model(model_path)
    
    # Get reconstruction of the file using the trained model
    reconstructed = autoencoder.predict(file_sequence_reshaped)
    
    # Calculate reconstruction error (Mean Squared Error)
    reconstruction_error = np.mean(np.abs(file_sequence - reconstructed.flatten()))
    
    # Define the threshold for anomaly detection (use the percentile of the reconstruction errors)
    threshold = threshold_percentile / 100  # Convert percentile to a value between 0 and 1
    
    # Print the reconstruction error and threshold for anomaly detection
    print(f"Reconstruction error: {reconstruction_error:.4f}")
    print(f"Threshold for anomaly detection: {threshold:.4f}")
    
    # Check if the file is an anomaly based on reconstruction error exceeding the threshold
    if reconstruction_error > threshold:
        print("The file is an anomaly (Good).")
    else:
        print("The file is normal (Bad).")

def main():
    # Check if a file path is passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python anomaly_detection.py <file_path>")
        sys.exit(1)
    
    # Get the file path from command line arguments
    file_path = sys.argv[1]
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    
    # Run the anomaly detection on the provided file
    run_anomaly_detection(file_path)

if __name__ == "__main__":
    main()
