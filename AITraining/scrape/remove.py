import os

# Specify the directory you want to scan
directory = '/mnt/shared/non-polyglots/'

# Loop through all files in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    
    # Check if it's a file and its size is 256 bytes
    if os.path.isfile(file_path) and os.path.getsize(file_path) < 256:
        os.remove(file_path)
        print(f"Removed: {file_path}")
