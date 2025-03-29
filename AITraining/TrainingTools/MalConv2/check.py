import os
import numpy as np

def check_file_sizes(file_path):
    """Check the actual size of the file after loading and padding."""
    file_bytes = read_file_bytes(file_path, max_size=1000000)
    print(f"File: {file_path} | Actual size: {len(file_bytes)} | Padded size: {len(file_bytes)}")

# Example usage for debugging
check_file_sizes("/data/processed/X_non-polyglots.npy")
check_file_sizes("/data/processed/X_polyglots.npy")
