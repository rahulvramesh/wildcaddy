#!/bin/bash

# Exit on any error
set -e

# Create a temporary folder to prepare the DMG contents
TMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TMP_DIR"

# Copy the app bundle to the temporary folder
echo "Copying WildCaddy.app to temporary directory..."
cp -R ./dist/WildCaddy.app "$TMP_DIR"/ || { echo "Failed to copy WildCaddy.app"; exit 1; }

# Create a symbolic link to the Applications folder
echo "Creating symlink to Applications folder..."
ln -s /Applications "$TMP_DIR/Applications" || { echo "Failed to create Applications symlink"; exit 1; }

# Create the DMG
echo "Creating DMG..."
hdiutil create -volname "WildCaddy" -srcfolder "$TMP_DIR" -ov -format UDZO WildCaddy.dmg || { echo "Failed to create DMG"; exit 1; }

# Clean up
echo "Cleaning up..."
rm -rf "$TMP_DIR"

echo "DMG creation completed successfully."