import os
import random
import subprocess

SOURCE_DIR = '/mnt/shared/downloads'  # Root directory containing the dataset
OUTPUT_DIR = '/mnt/shared/polyglots'  # Directory to save the polyglots

# Supported combinations for Mitra
supported_combinations = [
    ("pdf", "png"), ("pdf", "tiff"), ("pdf", "zip"), ("pdf", "7z"), ("pdf", "rar"),
    ("pdf", "iso"), ("pdf", "tar"), ("pdf", "ps"), ("pdf", "mp4"), ("pdf", "ar"),
    ("pdf", "bmp"), ("pdf", "bz2"), ("pdf", "cab"), ("pdf", "flac"), ("pdf", "gif"),
    ("pdf", "gz"), ("pdf", "ico"), ("pdf", "jpg"), ("pdf", "ogg"), ("pdf", "psd"),
    ("pdf", "rtf"), ("pdf", "bpg"), ("pdf", "java"), ("pdf", "pcap"), ("pdf", "xz"),
    ("png", "pdf"), ("tiff", "pdf"), ("zip", "pdf"), ("7z", "pdf"), ("rar", "pdf"),
    ("iso", "pdf"), ("tar", "pdf"), ("ps", "pdf"), ("mp4", "pdf"), ("ar", "pdf"),
    ("bmp", "pdf"), ("bz2", "pdf"), ("cab", "pdf"), ("flac", "pdf"), ("gif", "pdf"),
    ("gz", "pdf"), ("ico", "pdf"), ("jpg", "pdf"), ("ogg", "pdf"), ("psd", "pdf"),
    ("rtf", "pdf"), ("bpg", "pdf"), ("java", "pdf"), ("pcap", "pdf"), ("xz", "pdf"),
    # You can expand or modify this list with additional supported combinations
]

def create_polyglot(file_1, file_2, output_file):
    """Create a polyglot file by combining two different file formats using Mitra via the command line."""
    try:
        # Use absolute path to Python and mitra.py script
        python_executable = '/home/dmay/myenv/bin/python'  # Change to your Python executable path
        mitra_script = '/home/dmay/dillyDefender/AITraining/glotCreation/mitra/mitra.py'  # Full path to mitra.py
        
        command = [python_executable, mitra_script, file_1, file_2, "-o", OUTPUT_DIR , '-f']
        print(f"Running command: {command}")  # Full command list
        subprocess.run(command, check=True)
        print(f"Created polyglot: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating polyglot from {file_1} and {file_2}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def get_random_file(extension):
    """Get a random file from the source directory and its subdirectories with the given extension."""
    files = []
    
    # Walk through the directories and find all files with the required extension
    for root, dirs, files_in_dir in os.walk(SOURCE_DIR):
        for file in files_in_dir:
            if file.endswith(extension):
                files.append(os.path.join(root, file))
    
    if not files:
        print(f"No files found for extension: {extension}")
        return None
    
    # Return a random file from the list of found files
    return random.choice(files)

def generate_polyglots():
    """Generate polyglot files from the dataset."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Iterate through the supported combinations
    for ext_1, ext_2 in supported_combinations:
        file_1 = get_random_file(ext_1)
        file_2 = get_random_file(ext_2)

        if file_1 and file_2:
            output_file = OUTPUT_DIR
            create_polyglot(file_1, file_2, output_file)

if __name__ == "__main__":
    generate_polyglots()
