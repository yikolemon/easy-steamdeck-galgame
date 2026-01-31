#!/bin/bash

# Flatpak Build Script for SteamDeck GAL Game Helper
# This script builds and packages the application as a Flatpak

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_ID="io.github.steamdeck_galgame"
MANIFEST="io.github.steamdeck_galgame.json"
BUILD_DIR="flatpak-build"
REPO_DIR="flatpak-repo"
OUTPUT_FILE="${APP_ID}.flatpak"
BUNDLE_DIR="bundle"

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
print_header "Checking prerequisites"

command -v flatpak >/dev/null 2>&1 || { print_error "flatpak is not installed"; exit 1; }
print_success "flatpak found"

command -v flatpak-builder >/dev/null 2>&1 || { print_error "flatpak-builder is not installed"; exit 1; }
print_success "flatpak-builder found"

# Add Flathub repository if needed
print_header "Setting up Flatpak repositories"
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
print_success "Flathub repository configured"

# Validate manifest
print_header "Validating manifest"
if ! python3 -m json.tool "$MANIFEST" > /dev/null 2>&1; then
    print_error "Manifest validation failed"
    exit 1
fi
print_success "Manifest is valid JSON"

# Check manifest structure
python3 << 'PYEOF'
import json
import sys

with open('io.github.steamdeck_galgame.json') as f:
    manifest = json.load(f)

required = ['app-id', 'runtime', 'runtime-version', 'sdk', 'command', 'modules']
for key in required:
    if key not in manifest:
        print(f'Missing required key: {key}')
        sys.exit(1)

print(f"App ID: {manifest['app-id']}")
print(f"Runtime: {manifest['runtime']} {manifest['runtime-version']}")
print(f"Command: {manifest['command']}")
print(f"Modules: {len(manifest['modules'])}")
PYEOF

print_success "Manifest structure is valid"

# Clean up previous builds
print_header "Preparing build directories"
rm -rf "$BUILD_DIR" "$REPO_DIR" "$BUNDLE_DIR" "$OUTPUT_FILE"
mkdir -p "$BUILD_DIR" "$REPO_DIR" "$BUNDLE_DIR"
print_success "Build directories ready"

# Build Flatpak
print_header "Building Flatpak"
echo "This may take a few minutes..."

if flatpak-builder \
    --verbose \
    --repo="$REPO_DIR" \
    --force-clean \
    "$BUILD_DIR" \
    "$MANIFEST"; then
    print_success "Flatpak build completed"
else
    print_error "Flatpak build failed"
    exit 1
fi

# Create bundle
print_header "Creating Flatpak bundle"
if flatpak build-bundle \
    "$REPO_DIR" \
    "$OUTPUT_FILE" \
    "$APP_ID"; then
    print_success "Flatpak bundle created"
else
    print_error "Failed to create Flatpak bundle"
    exit 1
fi

# Generate metadata
print_header "Generating build metadata"
python3 << 'PYEOF'
import json
import os
from pathlib import Path

with open('io.github.steamdeck_galgame.json') as f:
    manifest = json.load(f)

flatpak_file = Path('io.github.steamdeck_galgame.flatpak')
if flatpak_file.exists():
    size_mb = flatpak_file.stat().st_size / (1024 * 1024)
else:
    size_mb = 0

metadata = {
    'app_id': manifest['app-id'],
    'version': manifest.get('metadata', {}).get('version', 'unknown'),
    'runtime': manifest['runtime'],
    'runtime_version': manifest['runtime-version'],
    'file_size_mb': round(size_mb, 2),
    'build_timestamp': os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip()
}

with open('build-metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(json.dumps(metadata, indent=2))
PYEOF

print_success "Build metadata generated"

# Display results
print_header "Build Summary"
echo -e "✅ Package: ${GREEN}$OUTPUT_FILE${NC}"
du -h "$OUTPUT_FILE" | awk '{print "📦 Size: " $1}'

echo -e "\n${BLUE}=== Installation Instructions ===${NC}"
echo "1. Local installation (offline):"
echo "   flatpak install $OUTPUT_FILE"
echo ""
echo "2. Run the application:"
echo "   flatpak run $APP_ID"
echo ""
echo "3. Or install from Flathub (online):"
echo "   flatpak install flathub $APP_ID"

print_success "Build completed successfully!"
