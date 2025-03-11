#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory does not exist."
    exit 1
fi

mkdir -p "$DEST_DIR"

find "$SOURCE_DIR" -type f -exec cp {} "$DEST_DIR" \;

echo "All files copied successfully from $SOURCE_DIR to $DEST_DIR."
