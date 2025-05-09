import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import argparse 
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

print("starting")

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

def extract_features_from_chunk(chunk_data):
    try:
        features = np.frombuffer(chunk_data, dtype=np.uint8) / 255.0
        return features
    except Exception as e:
        print(f"Error extracting chunk features: {e}")
        return None

def classify_file(model, file_path, chunk_size=256, num_threads=4):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        if len(data) < chunk_size:
            print(f"Skipping {file_path}: File too small for chunking")
            return None

        num_chunks = len(data) // chunk_size
        chunks = [data[i * chunk_size: (i + 1) * chunk_size] for i in range(num_chunks)]

        # Extract features in parallel using ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            features_list = list(executor.map(extract_features_from_chunk, chunks))

        # Filter out None and pad features
        max_length = model.input_shape[1]
        processed = [
            np.pad(features, (0, max_length - len(features)), mode="constant").reshape(max_length, 1)
            for features in features_list if features is not None
        ]

        if not processed:
            print("No valid features extracted.")
            return None

        input_batch = np.stack(processed)
        predictions = model.predict(input_batch)
        avg_prediction = np.mean(predictions)
        return avg_prediction

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Polyglot Detector")
    parser.add_argument("-F", "--file", required=True, help="Path to the file to classify")
    
    args = parser.parse_args()
    print("Starting classification..." + args.file)
    if not os.path.exists(args.file):
        print(f"File {args.file} does not exist.")
        return
    current_dir = Path(__file__).resolve().parent
    model_path = current_dir / "polyglot_cnn_detector_best.h5"
    
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        return

    model = keras.models.load_model(str(model_path))

    prediction = classify_file(model, args.file)
    if prediction is not None:
        print(f"Prediction for {args.file}: {prediction}")
        if prediction > 0.5:
            print(f"The file {args.file} is predicted as Polyglot.")
        else:
            print(f"The file {args.file} is predicted as Non-Polyglot.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
