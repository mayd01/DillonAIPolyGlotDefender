import os
import random
import subprocess

SOURCE_DIR = '/mnt/shared/downloads'  # Root directory containing the dataset
OUTPUT_DIR = '/mnt/shared/polyglots'  # Directory to save the polyglots

# Supported combinations from the dataset (Stack, Parasite, Cavity, Zipper)
supported_combinations = [
    ("gif", "jar"), ("gif", "iso"), ("pe", "jar"), ("pe", "zip"),
    ("jpg", "zip"), ("jpg", "jar"), ("png", "zip"), ("png", "jar"),
    ("dcm", "iso"), ("dcm", "zip"), ("tiff", "iso"), ("tiff", "zip"),
    ("tiff", "pdf"), ("png", "pdf"), ("dcm", "pdf"), ("dcm", "jar"),
    ("png", "iso"), ("pe", "iso"), ("dcm", "gif")
]

def create_polyglot(file_1, file_2, output_file):
    """Create a polyglot file by combining two different file formats using Mitra via the command line."""
    try:
        python_executable = '/home/dmay/myenv/bin/python'  # Change to your Python executable path
        mitra_script = '/home/dmay/dillyDefender/AITraining/glotCreation/mitra/mitra.py'  # Full path to mitra.py
        
        command = [python_executable, mitra_script, file_1, file_2, "-o", output_file, '-f']
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"Created polyglot: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating polyglot from {file_1} and {file_2}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def get_random_file(extension):
    """Get a random file from the specific folder of the given extension."""
    ext_dir = os.path.join(SOURCE_DIR, extension)  # Look inside the specific folder

    if not os.path.exists(ext_dir) or not os.path.isdir(ext_dir):
        print(f"Directory not found for extension: {extension}")
        return None

    files = [os.path.join(ext_dir, file) for file in os.listdir(ext_dir) if file.endswith(f".{extension}")]

    if not files:
        print(f"No files found for extension: {extension}")
        return None
    
    return random.choice(files)


def generate_polyglots():
    """Generate polyglot files from the dataset."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for ext_1, ext_2 in supported_combinations:
        file_1 = get_random_file(ext_1)
        file_2 = get_random_file(ext_2)

        if file_1 and file_2:
            output_file = os.path.join(OUTPUT_DIR, f"{os.path.basename(file_1)}_{os.path.basename(file_2)}")
            create_polyglot(file_1, file_2, output_file)

if __name__ == "__main__":
    generate_polyglots()
