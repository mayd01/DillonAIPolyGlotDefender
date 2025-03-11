import os
import mimetypes
import csv
from PIL import Image
import zipfile
import tarfile
import rarfile
import PyPDF2
import magic  # python-magic library for MIME type detection
from pathlib import Path

file_extensions = [
    "pdf", "png", "tiff", "zip", "7z", "rar", "iso", 
    "tar", "ps", "mp4", "ar", "bmp", "bz2", "cab", "flac", 
    "gif", "gz", "ico", "jpg", "ogg", "psd", "rtf", "bpg", 
    "java", "pcap", "xz", "csv", "txt", "json", "xml", "jpeg", "jar" , "docx", "pptx", "xlsx", "doc", "ppt", "xls"
]

def validate_pdf_file(filepath):
    try:
        with open(filepath, 'rb') as file:
            PyPDF2.PdfFileReader(file)
        return True
    except Exception as e:
        print(f"Invalid PDF file {filepath}: {e}")
        return False

def validate_image_file(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()  # Verify the image is not corrupted
        return True
    except Exception as e:
        print(f"Invalid image file {filepath}: {e}")
        return False

def validate_zip_file(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.testzip()  # Test if the zip file is valid
        return True
    except Exception as e:
        print(f"Invalid ZIP file {filepath}: {e}")
        return False

def validate_tar_file(filepath):
    try:
        with tarfile.open(filepath, 'r') as tar_ref:
            tar_ref.getnames()  # Read the tar file contents
        return True
    except Exception as e:
        print(f"Invalid TAR file {filepath}: {e}")
        return False

def validate_rar_file(filepath):
    try:
        with rarfile.RarFile(filepath, 'r') as rar_ref:
            rar_ref.testzip()  # Test if the rar file is valid
        return True
    except Exception as e:
        print(f"Invalid RAR file {filepath}: {e}")
        return False

def validate_media_file(filepath):
    try:
        # Check if media files like mp4, ogg, flac are valid
        mime_type = magic.Magic(mime=True).from_file(filepath)
        if mime_type.startswith('audio/') or mime_type.startswith('video/'):
            return True
        return False
    except Exception as e:
        print(f"Invalid media file {filepath}: {e}")
        return False

def validate_file(filepath):
    # Extract the file extension
    ext = Path(filepath).suffix[1:].lower()

    # Validate file types based on the file extension
    if ext == 'pdf':
        return validate_pdf_file(filepath)
    elif ext in ['png', 'tiff', 'bmp', 'gif', 'jpg', 'ico']:
        return validate_image_file(filepath)
    elif ext == 'zip':
        return validate_zip_file(filepath)
    elif ext == 'tar':
        return validate_tar_file(filepath)
    elif ext == 'rar':
        return validate_rar_file(filepath)
    elif ext == 'mp4' or ext == 'ogg' or ext == 'flac':
        return validate_media_file(filepath)
    else:
        print(f"Unsupported file type for validation: {ext}")
        return False

def validate_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            filepath = os.path.join(root, file)
            if validate_file(filepath):
                print(f"Valid file: {filepath}")
            else:
                print(f"Invalid file: {filepath}")
                try:
                    os.remove(filepath)  # Delete the invalid file
                    print(f"Deleted invalid file: {filepath}")
                except Exception as e:
                    print(f"Error deleting file {filepath}: {e}")

if __name__ == "__main__":
    directory_path = input("Enter the directory to check: ")
    validate_directory(directory_path)
