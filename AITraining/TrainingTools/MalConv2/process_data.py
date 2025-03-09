import os
import numpy as np

def read_file_bytes(file_path, max_size=1000000):
    """Reads a file as bytes and pads it to max_size."""
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))  
    return np.frombuffer(file_bytes, dtype=np.uint8)  
def load_and_preprocess_data(directory, max_size=1000000):
    """Loads and preprocesses files from a directory and prepares labels."""
    files = []
    labels = []
    
    sub_dirs = ["non-polyglots", "polyglots"]
    
    for label, sub_dir in enumerate(sub_dirs):
        folder = os.path.join(directory, sub_dir)
        
        if not os.path.isdir(folder):
            print(f"Warning: Directory '{folder}' not found.")
            continue
        
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            
            if os.path.isdir(file_path):
                continue
                
            file_bytes = read_file_bytes(file_path, max_size)
            files.append(file_bytes)
            labels.append(label) 
    
    files = np.array(files)
    labels = np.array(labels)
    
    return files, labels

def preprocess_and_save_data(input_directory, output_directory, max_size=1000000):
    """Preprocess data and save it as npy files."""
    X, y = load_and_preprocess_data(input_directory, max_size)
    
    os.makedirs(output_directory, exist_ok=True)
    
    np.save(os.path.join(output_directory, "X.npy"), X)
    np.save(os.path.join(output_directory, "y.npy"), y)

    print(f"Preprocessing complete. Data saved to {output_directory}")

if __name__ == "__main__":
    input_directory = "./mnt/shared"
    output_directory = "./data/processed"
    
    preprocess_and_save_data(input_directory, output_directory)
