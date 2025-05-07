#!/bin/bash

APP_NAME="dilly_defender"
VERSION="1.0.0"
RELEASE="1"
RPMBUILD_DIR=~/rpmbuild
SRC_DIR=$RPMBUILD_DIR/SOURCES
SPEC_DIR=$RPMBUILD_DIR/SPECS
BUILD_DIR=$APP_NAME-$VERSION
BIN_PATH="target/x86_64-unknown-linux-musl/release/"
LIBS_PATH="target/release/deps"
CLAMAV_RPM="clamav-1.4.2.linux.x86_64.rpm"
CLAMAV_DEB="clamav-1.4.2.linux.x86_64.deb"
CLAMAV_URL_RPM="https://www.clamav.net/downloads/clamav-1.4.2.linux.x86_64.rpm"
CLAMAV_URL_DEB="https://www.clamav.net/downloads/clamav-1.4.2.linux.x86_64.deb"

# Create necessary directories
mkdir -p $SRC_DIR $SPEC_DIR

# Build the project using cargo
cargo build --release --target x86_64-unknown-linux-musl || { echo "Rust build failed"; exit 1; }

# Clean up previous build and create the new build directory structure
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/bin
mkdir -p $BUILD_DIR/libs

# Copy the binary and libraries into the build directory
cp $BIN_PATH/* $BUILD_DIR/bin/
cp $LIBS_PATH/*.so $BUILD_DIR/libs/

# Compress the build directory into a tarball
tar czvf $APP_NAME.tar.gz $BUILD_DIR
mv $APP_NAME.tar.gz $SRC_DIR/

# Generate the RPM spec file
cat > $SPEC_DIR/$APP_NAME.spec <<EOF
Name:           $APP_NAME
Version:        $VERSION
Release:        $RELEASE%{?dist}
Summary:        A Rust-based application for PolyGlot File Detection

License:        MIT
URL:            https://defender.dillonmay.com
BuildArch:      x86_64
Source0:        %{name}.tar.gz

%description
$APP_NAME is a Rust-based application designed for PolyGlot File Detection.

%prep
%setup -q

%build
# No build step needed as the binary is prebuilt

%install
# Install the executable under /opt/DillyDefender/bin
mkdir -p %{buildroot}/opt/DillyDefender/bin
install -m 755 $BUILD_DIR/bin/* %{buildroot}/opt/DillyDefender/bin/

# Install the libraries under /opt/DillyDefender/libs
mkdir -p %{buildroot}/opt/DillyDefender/libs
install -m 755 $BUILD_DIR/libs/* %{buildroot}/opt/DillyDefender/libs/

%files
/opt/DillyDefender/bin/*  
/opt/DillyDefender/libs/*

%changelog
EOF

# Build the RPM package
rpmbuild -ba $SPEC_DIR/$APP_NAME.spec || { echo "RPM build failed"; exit 1; }

echo "RPM built successfully!"
echo "Find your RPM at: $RPMBUILD_DIR/RPMS/x86_64/"

# Move the built RPM to the specified directory
mv $RPMBUILD_DIR/RPMS/x86_64/$APP_NAME-$VERSION-$RELEASE.x86_64.rpm /home/dmay/DillyEnterpriseCloud/

# Install ClamAV
echo "Installing ClamAV..."

# Check if ClamAV RPM or DEB exists; if not, download it
if [ ! -f "$CLAMAV_RPM" ] && [ ! -f "$CLAMAV_DEB" ]; then
    echo "ClamAV package not found, downloading..."

    # Check if it's a RHEL or Ubuntu system to download the appropriate package
    if [ -f /etc/redhat-release ]; then
        # For RHEL, download the .rpm package
        wget $CLAMAV_URL_RPM -O $CLAMAV_RPM || { echo "Failed to download ClamAV RPM"; exit 1; }
    elif [ -f /etc/lsb-release ] || [ -f /etc/ubuntu-release ]; then
        # For Ubuntu, download the .deb package
        wget $CLAMAV_URL_DEB -O $CLAMAV_DEB || { echo "Failed to download ClamAV DEB"; exit 1; }
    else
        echo "Unsupported system. Please download the ClamAV package manually."
        exit 1
    fi
fi

# For RHEL systems, use rpm to install ClamAV
if [ -f "$CLAMAV_RPM" ]; then
    sudo rpm -ivh $CLAMAV_RPM
    echo "ClamAV installed successfully!"
    
    # Move ClamAV to /opt/DillyDefender/clamav
    sudo mv /usr/local/bin/clamd /opt/DillyDefender/clamav/
    sudo mv /usr/local/bin/clamscan /opt/DillyDefender/clamav/
    sudo mv /usr/local/lib/clamav /opt/DillyDefender/clamav/
    sudo mv /etc/clamav /opt/DillyDefender/clamav/

    sudo chown -R root:root /opt/DillyDefender/clamav
    sudo chmod -R 755 /opt/DillyDefender/clamav

elif [ -f "$CLAMAV_DEB" ]; then
    # For Ubuntu systems, use dpkg to install ClamAV
    sudo dpkg -i $CLAMAV_DEB
    echo "ClamAV installed successfully!"
    
    # Move ClamAV to /opt/DillyDefender/clamav
    sudo mv /usr/local/bin/clamd /opt/DillyDefender/clamav/
    sudo mv /usr/local/bin/clamscan /opt/DillyDefender/clamav/
    sudo mv /usr/local/lib/clamav /opt/DillyDefender/clamav/
    sudo mv /etc/clamav /opt/DillyDefender/clamav/

    sudo chown -R root:root /opt/DillyDefender/clamav
    sudo chmod -R 755 /opt/DillyDefender/clamav

else
    echo "ClamAV package not found. Please download the appropriate .rpm or .deb file."
    exit 1
fi

echo "ClamAV installed to /opt/DillyDefender/clamav"
