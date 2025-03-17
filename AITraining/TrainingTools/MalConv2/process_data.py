import os
import numpy as np

def read_file_bytes(file_path, max_size=1000000):
    """Reads a file as bytes and pads it to max_size."""
    print(f"Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    if len(file_bytes) < max_size:
        file_bytes = file_bytes + b'\0' * (max_size - len(file_bytes))  
    return file_bytes  # Return raw byte data

def load_and_preprocess_data(directory, max_size=1000000, batch_size=10):
    """Loads and preprocesses files from a directory and prepares labels."""
    print(f"Starting to load and preprocess data from directory: {directory}")
    
    # Initialize lists to hold files and labels in the current batch
    files_batch = []
    labels_batch = []
    
    sub_dirs = ["non-polyglots", "polyglots"]
    print("Found the subdirectories:", sub_dirs)
    
    # Iterate through subdirectories
    for label, sub_dir in enumerate(sub_dirs):
        folder = os.path.join(directory, sub_dir)
        
        if not os.path.isdir(folder):
            print(f"Warning: Directory '{folder}' not found.")
            continue
        
        print(f"Processing folder: {folder}")
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            
            if os.path.isdir(file_path):
                print(f"Skipping directory: {file_path}")
                continue
                
            print(f"Processing file: {file_path}")
            file_bytes = read_file_bytes(file_path, max_size)
            files_batch.append(file_bytes)
            labels_batch.append(label)
            
            # If batch size is reached, save the batch to disk and reset batch containers
            if len(files_batch) >= batch_size:
                save_batch(files_batch, labels_batch, sub_dir)
                files_batch = []
                labels_batch = []
    
    # Save any remaining files in the last batch
    if files_batch:
        save_batch(files_batch, labels_batch, "remaining")
    
    print(f"Data loading complete.")

def save_batch(files_batch, labels_batch, batch_name, output_directory="/mnt/IronVault/processed"):
    """Saves a batch of processed files and labels to the specified directory."""
    os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists
    
    x_path = os.path.join(output_directory, f"X_{batch_name}.npy")
    y_path = os.path.join(output_directory, f"y_{batch_name}.npy")

    np.save(x_path, files_batch)
    np.save(y_path, labels_batch)

    print(f"Saved batch: {batch_name} -> {x_path}, {y_path}")


def preprocess_and_save_data(input_directory, output_directory, max_size=1000000, batch_size=10):
    """Preprocess data and save it as npy files in batches."""
    print(f"Starting preprocessing for directory: {input_directory}")
    load_and_preprocess_data(input_directory, max_size, batch_size)
    print("Data processing complete.")

if __name__ == "__main__":
    input_directory = "/mnt/IronVault"
    output_directory = "/mnt/IronVault/processed"
    
    print("Starting the preprocessing and saving process...")
    preprocess_and_save_data(input_directory, output_directory, batch_size=10)
    print("Process complete.")
