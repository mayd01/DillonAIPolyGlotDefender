import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import argparse 
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
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

def classify_chunk(model, chunk_data, max_length):
    try:
        features = extract_features_from_chunk(chunk_data)
        if features is None:
            return None

        features_padded = np.pad(features, (0, max_length - len(features)), mode="constant")
        features_padded = features_padded.reshape(1, max_length, 1)

        prediction = model.predict(features_padded)
        return prediction[0][0]
    
    except Exception as e:
        print(f"Error classifying chunk: {e}")
        return None

def classify_file(model, file_path, chunk_size=256, num_threads=4):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        if len(data) < chunk_size:
            print(f"Skipping {file_path}: File too small for chunking")
            return None

        chunk_predictions = []
        num_chunks = len(data) // chunk_size

        # Create a ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit classification tasks for each chunk
            futures = [
                executor.submit(classify_chunk, model, data[i * chunk_size: (i + 1) * chunk_size], model.input_shape[1])
                for i in range(num_chunks)
            ]

            # Collect the results from the threads
            for future in futures:
                result = future.result()
                if result is not None:
                    chunk_predictions.append(result)

        # Combine predictions (e.g., by averaging the scores)
        if chunk_predictions:
            avg_prediction = np.mean(chunk_predictions)
            return avg_prediction

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def extract_features_from_chunk(chunk_data):
    # You can extract features from the chunk data similarly to how you do it for the whole file
    features = np.frombuffer(chunk_data, dtype=np.uint8) / 255.0
    return features

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
