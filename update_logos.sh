#!/bin/bash

# Update favicon and logo references in all HTML files
find /home/chillop/Project/new-asanmagn-sit/Asamang-website -name "*.html" -type f -exec sed -i 's/href="assets\/img\/favicon\.png"/href="assets\/img\/asamang-logo\.png"/g' {} \;
find /home/chillop/Project/new-asanmagn-sit/Asamang-website -name "*.html" -type f -exec sed -i 's/href="assets\/img\/apple-touch-icon\.png"/href="assets\/img\/asamang-logo\.png"/g' {} \;
find /home/chillop/Project/new-asanmagn-sit/Asamang-website -name "*.html" -type f -exec sed -i 's/src="assets\/img\/logo\.webp"/src="assets\/img\/asamang-logo\.png"/g' {} \;

echo "Logo and favicon references have been updated in all HTML files."
