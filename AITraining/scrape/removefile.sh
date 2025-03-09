#!/bin/bash

# Define valid extensions for pdf and other file types
valid_extensions=(
    "pdf" "png" "tiff" "zip" "7z" "rar"
    "iso" "tar" "ps" "mp4" "ar" "bmp"
    "bz2" "cab" "flac" "gif" "gz" "ico"
    "jpg" "ogg" "psd" "rtf" "bpg" "java"
    "pcap" "xz"
)

for dir in */; do
    folder_name="${dir%/}"

    is_valid=false

    for ext in "${valid_extensions[@]}"; do
        if ls "$dir"/*."$ext" > /dev/null 2>&1; then
            is_valid=true
            break
        fi
    done

    if [ "$is_valid" = false ]; then
        echo "Removing invalid folder: $folder_name"
        rm -rf "$dir"
    fi
done
