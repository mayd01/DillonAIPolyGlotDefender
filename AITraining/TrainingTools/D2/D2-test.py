import os
import numpy as np
import tensorflow as tf
from tensorflow import keras

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

model = keras.models.load_model("polyglot_cnn_detector_final.h5")

max_length = model.input_shape[1]

def test_file(file_path):
    features = extract_features(file_path)
    if features is not None:
        features_padded = np.pad(features, (0, max_length - len(features)), mode='constant')
        features_padded = features_padded.reshape(1, max_length, 1)
        
        prediction = model.predict(features_padded)[0][0]
        print(f"\nFile: {file_path}")
        print(f"Prediction Score: {prediction:.4f}")
        print("Polyglot Detected!" if prediction >= 0.5 else " Not a Polyglot File")
    else:
        print("Feature extraction failed.")

if __name__ == "__main__":
    file_path = input("Enter the path of the file to test: ").strip()
    if os.path.exists(file_path):
        test_file(file_path)
    else:
        print("Invalid file path. Please check and try again.")
