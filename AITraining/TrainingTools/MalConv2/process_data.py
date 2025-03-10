import os
import numpy as np

# Function to read bytes from a file and pad it to a fixed size
def read_file_bytes(file_path, max_size=1000000):
    """Reads a file as bytes and pads it to max_size."""
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))  # Pad with zeros
    return np.frombuffer(file_bytes, dtype=np.uint8)  # Convert bytes to numpy array

# Function to load and preprocess the dataset
def load_and_preprocess_data(directory, max_size=1000000):
    """Loads and preprocesses files from a directory and prepares labels."""
    files = []
    labels = []
    
    for label, sub_dir in enumerate(["non-polyglots", "polyglots"]):
        folder = os.path.join(directory, sub_dir)
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            file_bytes = read_file_bytes(file_path, max_size)
            files.append(file_bytes)
            labels.append(label)  # 0 for non-polyglot, 1 for polyglot
    
    # Convert to numpy arrays for training
    files = np.array(files)
    labels = np.array(labels)
    
    return files, labels

# Main function to preprocess the data and save it
def preprocess_and_save_data(input_directory, output_directory, max_size=1000000):
    """Preprocess data and save it as npy files."""
    X, y = load_and_preprocess_data(input_directory, max_size)
    
    # Save the preprocessed data
    np.save(os.path.join(output_directory, "X.npy"), X)
    np.save(os.path.join(output_directory, "y.npy"), y)

    print(f"Preprocessing complete. Data saved to {output_directory}")

if __name__ == "__main__":
    input_directory = "./data"
    output_directory = "./data/processed"
    os.makedirs(output_directory, exist_ok=True)
    preprocess_and_save_data(input_directory, output_directory)
