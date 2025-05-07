
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import argparse
from pathlib import Path
from pathlib import Path

# Disable GPU usage and suppress logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

print("starting")

def extract_features(data):
    """Normalize byte data to float32 [0, 1]"""
    return data.astype(np.float32) / 255.0

def classify_file(model, file_path, chunk_size=256):
    try:
        # Load and convert file to NumPy array of uint8
        with open(file_path, "rb") as f:
            byte_data = f.read()
        if len(byte_data) < chunk_size:
            print(f"Skipping {file_path}: File too small for chunking")
            return None

        input_length = model.input_shape[1]
        num_chunks = len(byte_data) // chunk_size

        # Vectorized feature extraction and padding
        chunks = [
            extract_features(
                np.frombuffer(byte_data[i * chunk_size:(i + 1) * chunk_size], dtype=np.uint8)
            )
            for i in range(num_chunks)
        ]
        chunks_padded = np.array([
            np.pad(chunk, (0, input_length - len(chunk)), mode="constant")
            for chunk in chunks
        ]).reshape(num_chunks, input_length, 1)

        # Batch prediction
        predictions = model.predict(chunks_padded, batch_size=32, verbose=0)
        return float(np.mean(predictions)) if predictions.size > 0 else None

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Polyglot Detector")
    parser.add_argument("-F", "--file", required=True, help="Path to the file to classify")
    args = parser.parse_args()

    current_dir = Path(__file__).resolve().parent
    
    model_path = current_dir / "polyglot_cnn_detector_best.h5"
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        return

    model = keras.models.load_model(str(model_path))

    # Predict
    file_path = args.file
    prediction = classify_file(model, file_path)

    if prediction is None:
        print("Prediction failed.")
        return

    print(f"Prediction for {file_path}: {prediction:.4f}")
    if prediction > 0.5:
        print(f"The file {file_path} is predicted as Polyglot.")
    else:
        print(f"The file {file_path} is predicted as Non-Polyglot.")

if __name__ == "__main__":
    main()
