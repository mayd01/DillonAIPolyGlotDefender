# classify_files.py

import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_model():
    """Load the trained LSTM model."""
    return tf.keras.models.load_model("trained_lstm_model.h5")

def extract_features(file_path, regions=[(0, 256), (-256, None)]):
    """
    Extract features from binary files by slicing specific regions.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        if len(data) < 256:
            print(f"Skipping {file_path}: File too small")
            return None
        
        features = [data[start:end] if end is not None else data[start:] for start, end in regions]
        return np.concatenate([np.frombuffer(f, dtype=np.uint8) / 255.0 for f in features])
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def classify_file(file_path, model, max_length):
    """
    Classify a file using the trained model.
    """
    features = extract_features(file_path)
    
    if features is None:
        print(f"Skipping {file_path}: Unable to extract features.")
        return None
    
    padded_features = pad_sequences([features], maxlen=max_length, padding='post')

    prediction = model.predict(padded_features)

    predicted_class = np.argmax(prediction, axis=-1)
    return predicted_class[0]

def classify_files_in_directory(folder_to_classify, max_length):
    """
    Classify all files in a given directory using the trained model.
    """
    model = load_model()

    for file_name in os.listdir(folder_to_classify):
        file_path = os.path.join(folder_to_classify, file_name)
        predicted_class = classify_file(file_path, model, max_length)
        
        if predicted_class is not None:
            print(f"File: {file_name}, Predicted Class: {predicted_class}")
        else:
            print(f"File: {file_name}, Classification failed.")

if __name__ == "__main__":
    folder_to_classify = "/data/polyglots" 
    max_length = 512  
    classify_files_in_directory(folder_to_classify, max_length)
