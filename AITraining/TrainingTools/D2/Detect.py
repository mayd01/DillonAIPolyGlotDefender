import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import argparse

def extract_features(file_path, regions=[(0, 256), (-256, None)]):
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

def classify_file(model, file_path):
    features = extract_features(file_path)
    if features is None:
        print(f"Cannot classify {file_path}.")
        return None

    max_length = model.input_shape[1]  
    features_padded = np.pad(features, (0, max_length - len(features)), mode="constant")
    features_padded = features_padded.reshape(1, max_length, 1)

    prediction = model.predict(features_padded)
    return prediction[0][0]

def main():
    parser = argparse.ArgumentParser(description="Polyglot Detector")
    parser.add_argument("-F", "--file", required=True, help="Path to the file to classify")
    args = parser.parse_args()

    model = keras.models.load_model("polyglot_cnn_detector_best.h5")

    file_path = args.file
    prediction = classify_file(model, file_path)
    print(f"Prediction for {file_path}: {prediction}")
    if prediction is not None:
        if prediction > 0.5:
            print(f"The file {file_path} is predicted as Polyglot.")
        else:
            print(f"The file {file_path} is predicted as Non-Polyglot.")

if __name__ == "__main__":
    main()
