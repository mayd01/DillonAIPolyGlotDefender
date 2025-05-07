#!/bin/bash

APP_NAME="dilly_defender"
PACKAGE_NAME=$(echo "$APP_NAME" | tr '_' '-') 
VERSION="v1.0.0"
ARCH="amd64"
BUILD_DIR="$PACKAGE_NAME-$VERSION"
DEB_DIR="$BUILD_DIR/DEBIAN"
BIN_PATH="target/release/$APP_NAME"
INSTALL_DIR="/opt/DillyDefender/bin"
CLAMAV_DIR="/opt/DillyDefender/clamav"
CLAMAV_URL="https://www.clamav.net/downloads/clamav-1.4.2.linux.x86_64.tar.gz" # Example URL, replace with the actual one you need
CLAMAV_TAR="clamav-1.4.2.linux.x86_64.tar.gz"  # Adjust with the appropriate filename

# Build the project using cargo

# Clean up previous build and create the new build directory structure
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR$INSTALL_DIR
mkdir -p $DEB_DIR

# Copy the binary into the build directory
cp $BIN_PATH $BUILD_DIR$INSTALL_DIR/

# Download and extract ClamAV
echo "Downloading ClamAV..."
wget -O $CLAMAV_TAR $CLAMAV_URL || { echo "ClamAV download failed"; exit 1; }

echo "Extracting ClamAV..."
tar -xzvf $CLAMAV_TAR -C $CLAMAV_DIR || { echo "ClamAV extraction failed"; exit 1; }

# Clean up the ClamAV tarball
rm -f $CLAMAV_TAR

# Create the control file for the Debian package
cat > $DEB_DIR/control <<EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: custom
Priority: optional
Architecture: $ARCH
Maintainer: Dillon May <help@defender.dillonmay.com>
Description: A Rust-based application for PolyGlot File Detection with ClamAV integration
Depends: libc6 (>= 2.28), clamav (>= 1.4.2)
Recommends: curl
Suggests: gzip, tar
Provides: $PACKAGE_NAME
Conflicts: $PACKAGE_NAME
EOF

# Create the postinst script to handle installation actions
cat > $DEB_DIR/postinst <<EOF
#!/bin/bash
# Post-installation script for $PACKAGE_NAME

# Ensure the directories exist
mkdir -p /opt/DillyDefender
mkdir -p /opt/DillyDefender/clamav

# Move the binary to the installation directory
cp -r $INSTALL_DIR /opt/DillyDefender/

# Set correct permissions for the files
chmod -R 755 /opt/DillyDefender

# Optionally, you can start ClamAV or other setup tasks here.

# Install ClamAV binary to /opt/DillyDefender/clamav
cp -r $CLAMAV_DIR/* /opt/DillyDefender/clamav/

# Set correct permissions for ClamAV
chmod -R 755 /opt/DillyDefender/clamav

EOF

# Make the postinst script executable
chmod +x $DEB_DIR/postinst

# Build the Debian package
dpkg-deb --build $BUILD_DIR || { echo "Deb package build failed"; exit 1; }

# Rename the package to the desired format
mv "$BUILD_DIR.deb" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Display success message
echo "Deb package built successfully!"
echo "Find your package at: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "To install, run: sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "To uninstall, run: sudo dpkg -r $PACKAGE_NAME"
echo "To remove all files, run: sudo dpkg -P $PACKAGE_NAME"
