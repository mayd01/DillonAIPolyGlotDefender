import os
import numpy as np
import pickle

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

def process_and_save_incrementally(polyglot_dir, non_polyglot_dir, output_file):
    """
    Process dataset incrementally and save after each file.
    """
    X, y = [], []
    max_length = 0
    
    for label, folder in enumerate([non_polyglot_dir, polyglot_dir]):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            print(f"Processing {file_path}...")
            features = extract_features(file_path)
            
            if features is not None:
                X.append(features)
                y.append(label)
                max_length = max(max_length, len(features))
                
                # Pad and save the dataset incrementally
                X_padded = np.array([np.pad(x, (0, max_length - len(x)), mode='constant') for x in X], dtype=np.float32)
                with open(output_file, 'wb') as f:
                    pickle.dump((X_padded, y, max_length), f)
                
                print(f"Saved progress to {output_file}")

if __name__ == "__main__":
    polyglot_dir = "/mnt/IronVault/polyglots"
    non_polyglot_dir = "/mnt/IronVault/non-polyglots"
    output_file = "/mnt/IronVault/processed/preprocessed_data.pkl"
    
    process_and_save_incrementally(polyglot_dir, non_polyglot_dir, output_file)