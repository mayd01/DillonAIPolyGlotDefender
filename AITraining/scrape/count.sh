#!/bin/bash

# Define the list of valid extensions
valid_extensions=(
    "pdf" "png" "tiff" "zip" "7z" "rar"
    "iso" "tar" "ps" "mp4" "ar" "bmp"
    "bz2" "cab" "flac" "gif" "gz" "ico"
    "jpg" "ogg" "psd" "rtf" "bpg" "java"
    "pcap" "xz"
)

# Set the folder variable (no space after the equal sign)
folder="/mnt/shared/downloads/"

# Loop through each subdirectory in the folder
for dir in "$folder"*/; do
    # Get the folder name without the trailing slash
    folder_name="${dir%/}"

    # Initialize a counter for the number of files in this folder
    total_files=0

    # Loop through the valid extensions and count files for each extension in the folder
    for ext in "${valid_extensions[@]}"; do
        file_count=$(find "$dir" -type f -name "*.$ext" | wc -l)
        total_files=$((total_files + file_count))
    done

    # Display the result if there are any files with valid extensions in the folder
    if [ "$total_files" -gt 0 ]; then
        echo "Folder: $folder_name - Total files: $total_files"
    fi
done
