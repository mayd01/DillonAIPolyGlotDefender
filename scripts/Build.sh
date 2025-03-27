#!/bin/bash

# Variables
DIST_DIR="dist"
BIN_DIR="$DIST_DIR/bin"
LIBS_DIR="$DIST_DIR/libs"
TARGET_DIR="target/release"
EXEC_NAME="Factory"

# Clean up any existing distribution folder
rm -rf $DIST_DIR
mkdir -p $BIN_DIR
mkdir -p $LIBS_DIR

# Build the project
echo "Building the Factory executable..."
cargo build --release

# Move the executable to the bin directory
cp $TARGET_DIR/$EXEC_NAME $BIN_DIR/

# Move the libraries to the libs directory
echo "Copying libraries..."
cp target/release/deps/*.so $LIBS_DIR/

# Optionally copy any other files needed for your project, e.g., config files
# cp path_to_additional_files/* $DIST_DIR/

# Package the directory into a tar.gz file
echo "Creating tar.gz distribution package..."
tar -czvf $DIST_DIR.tar.gz -C $DIST_DIR .

# Clean up build files
echo "Cleaning up..."
rm -rf $DIST_DIR

echo "Build complete! Distribution package created at: $DIST_DIR.tar.gz"
