#!/bin/bash

APP_NAME="dilly_defender"
VERSION="0.0.1.BETA"
RELEASE="1"
RPMBUILD_DIR=~/rpmbuild
SRC_DIR=$RPMBUILD_DIR/SOURCES
SPEC_DIR=$RPMBUILD_DIR/SPECS
BUILD_DIR=$APP_NAME-$VERSION
BIN_PATH="target/x86_64-unknown-linux-musl/release/$APP_NAME"
LIBS_PATH="target/release/deps"

mkdir -p $SRC_DIR $SPEC_DIR

cargo build --release --target x86_64-unknown-linux-musl || { echo "Rust build failed"; exit 1; }

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/bin
mkdir -p $BUILD_DIR/libs

cp $BIN_PATH $BUILD_DIR/bin/
cp $LIBS_PATH/*.so $BUILD_DIR/libs/

tar czvf $APP_NAME.tar.gz $BUILD_DIR
mv $APP_NAME.tar.gz $SRC_DIR/

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
# Install the executable
mkdir -p %{buildroot}/usr/local/bin
install -m 755 $APP_NAME %{buildroot}/usr/local/bin/$APP_NAME

# Install the libraries
mkdir -p %{buildroot}/usr/local/libs
install -m 755 $BUILD_DIR/libs/* %{buildroot}/usr/local/libs/

%files
/usr/local/bin/$APP_NAME
/usr/local/libs/*

%changelog
EOF

rpmbuild -ba $SPEC_DIR/$APP_NAME.spec || { echo "RPM build failed"; exit 1; }

echo "RPM built successfully!"
echo "Find your RPM at: $RPMBUILD_DIR/RPMS/x86_64/"

mv $RPMBUILD_DIR/RPMS/x86_64/$APP_NAME-$VERSION-$RELEASE.x86_64.rpm /home/dmay/DillyEnterpriseCloud/
