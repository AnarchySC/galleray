#!/bin/bash
# Galleray installer

set -e

echo "Installing Galleray..."

# Install Python dependency
pip install --user PyQt5

# Create install directory
sudo mkdir -p /opt/galleray
sudo cp galleray.py galleray.png galleray.svg /opt/galleray/
sudo chmod +x /opt/galleray/galleray.py

# Install desktop entry
cp galleray.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "Done! Galleray is now in your application menu."
