#!/bin/bash

# Download SWORD commentary modules and extract to assets/commentaries/

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$PROJECT_DIR/assets/commentaries"
TEMP_DIR=$(mktemp -d)

echo "Downloading SWORD commentary modules..."
echo "Temp directory: $TEMP_DIR"

# Create assets directory
mkdir -p "$ASSETS_DIR"

# SWORD module download URLs (from CrossWire mirrors)
declare -A MODULES=(
  ["Clarke"]="Clarke"
  ["JFB"]="JFB"
  ["RWP"]="RWP"
  ["MHCC"]="MHCC"
)

# CrossWire module repository URL
BASE_URL="http://crosswire.2517.com/sword/modules"

for MODULE in "${!MODULES[@]}"; do
  echo ""
  echo "Downloading $MODULE..."
  
  # Try multiple mirrors
  DOWNLOADED=false
  
  # Try primary mirror
  if curl -f -L "${BASE_URL}/${MODULE}.zip" -o "$TEMP_DIR/${MODULE}.zip" 2>/dev/null; then
    DOWNLOADED=true
    echo "✓ Downloaded $MODULE from primary mirror"
  fi
  
  # If primary failed, try alternative mirror
  if [ "$DOWNLOADED" = false ]; then
    ALT_URL="https://www.crosswire.org/ftplist.html"
    echo "Note: Could not download $MODULE from primary mirror."
    echo "Please visit https://www.crosswire.org/sword/modules/ to download ${MODULE}.zip manually"
    echo "and extract it to: $ASSETS_DIR/${MODULE}/"
  else
    # Extract to assets directory
    echo "Extracting $MODULE..."
    unzip -q "$TEMP_DIR/${MODULE}.zip" -d "$ASSETS_DIR/${MODULE}/"
    echo "✓ Extracted $MODULE to $ASSETS_DIR/${MODULE}/"
  fi
done

echo ""
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo ""
echo "Done! Commentary modules are in: $ASSETS_DIR"
echo ""
echo "Directory structure should be:"
echo "  assets/commentaries/"
echo "  ├── Clarke/"
echo "  ├── JFB/"
echo "  ├── RWP/"
echo "  └── MHCC/"
echo ""
echo "Next step: Convert the downloaded modules to JSON format."
