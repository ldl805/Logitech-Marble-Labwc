#!/bin/bash
# Script to build a Debian package for Logitech-Marble-Labwc

APP_NAME="logitech-marble-labwc"
VERSION="1.0"
PKG_DIR="${APP_NAME}_${VERSION}_all"

echo "Building Debian package $PKG_DIR..."

# Create structure
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"

# Create control file
cat <<EOF > "$PKG_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, labwc
Maintainer: ldl805 <ldl805@github.com>
Description: Logitech Trackman Marble Scroll Emulation for Labwc
 A configuration utility to enable scroll wheel emulation for the
 Logitech Trackman Marble (T-BC21) trackball in the Labwc Wayland compositor.
EOF

# Copy application files (rename install.py to the package name)
cp install.py "$PKG_DIR/usr/bin/$APP_NAME"
chmod 755 "$PKG_DIR/usr/bin/$APP_NAME"

# Build package
dpkg-deb --build --root-owner-group "$PKG_DIR"

echo "Package built: ${PKG_DIR}.deb"
