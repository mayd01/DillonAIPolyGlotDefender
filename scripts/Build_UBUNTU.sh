#!/bin/bash

APP_NAME="dilly_defender"
PACKAGE_NAME=$(echo "$APP_NAME" | tr '_' '-') 
VERSION="0.0.1.BETA"
ARCH="amd64"
BUILD_DIR="$PACKAGE_NAME-$VERSION"
DEB_DIR="$BUILD_DIR/DEBIAN"
BIN_PATH="target/release/$APP_NAME"
INSTALL_DIR="/usr/local/bin"

cargo build --release || { echo "Rust build failed"; exit 1; }

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR$INSTALL_DIR
mkdir -p $DEB_DIR

cp $BIN_PATH $BUILD_DIR$INSTALL_DIR/

cat > $DEB_DIR/control <<EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: custom
Priority: optional
Architecture: $ARCH
Maintainer: Dillon May help@defender.dillonmay.com
Description: A Rust-based application
 For PolyGlot File Detection 
EOF

dpkg-deb --build $BUILD_DIR || { echo "Deb package build failed"; exit 1; }

mv "$BUILD_DIR.deb" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo "Deb package built successfully!"
echo "Find your package at: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "To install, run: sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "To uninstall, run: sudo dpkg -r $PACKAGE_NAME"
echo "To remove all files, run: sudo dpkg -P $PACKAGE_NAME"