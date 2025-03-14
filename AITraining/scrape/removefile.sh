#!/bin/bash

# Define valid extensions for pdf and other file types
valid_extensions=(
    "pdf" "png" "tiff" "zip" "7z" "rar"
    "iso" "tar" "ps" "mp4" "ar" "bmp"
    "bz2" "cab" "flac" "gif" "gz" "ico"
    "jpg" "ogg" "psd" "rtf" "bpg" "java"
    "pcap" "xz" "jpeg" "mp3" "wav" "txt" "docx" "doc" "xls" "xlsx" "ppt" "pptx" "csv" "json" "zip" 
    "tar.gz" "tgz" "mp4" "mkv" "avi" "mov" "wmv" "flv" "webm" "mp3" "wav" "aac" "ogg" "flac"
    
)

# Define the parent directory to search in
parent_directory="/mnt/shared/downloads/"

# Change to the parent directory
cd "$parent_directory" || exit 1

for dir in */; do
    folder_name="${dir%/}"

    is_valid=false

    # Check for valid files with the specified extensions in the folder
    for ext in "${valid_extensions[@]}"; do
        if ls "$dir"/*."$ext" > /dev/null 2>&1; then
            is_valid=true
            break
        fi
    done

    # If the folder doesn't contain any valid file extensions, remove it
    if [ "$is_valid" = false ]; then
        echo "Removing invalid folder: $folder_name"
        rm -rf "$dir"
    fi
done
