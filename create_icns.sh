#!/bin/bash

# Create the icon set directory
mkdir WildCaddy.iconset

# Generate the various icon sizes
sips -z 16 16     resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_16x16.png
sips -z 32 32     resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_16x16@2x.png
sips -z 32 32     resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_32x32.png
sips -z 64 64     resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_32x32@2x.png
sips -z 128 128   resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_128x128.png
sips -z 256 256   resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_128x128@2x.png
sips -z 256 256   resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_256x256.png
sips -z 512 512   resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_256x256@2x.png
sips -z 512 512   resources/wild_caddy_icon.png --out WildCaddy.iconset/icon_512x512.png
cp  resources/wild_caddy_icon.png WildCaddy.iconset/icon_512x512@2x.png

# Create the icns file
iconutil -c icns WildCaddy.iconset

# Move the icns file to the resources folder
mv WildCaddy.icns resources/wild_caddy_icon.icns

# Clean up
rm -R WildCaddy.iconset