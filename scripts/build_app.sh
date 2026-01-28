#!/bin/bash

# Build Script for Kisan AI Frontend

echo "🏗️  Starting Kisan AI Build..."
echo "=============================="

PROJECT_ROOT=$(dirname "$(dirname "$(readlink -f "$0")")")
DIST_DIR="$PROJECT_ROOT/dist"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 1. Clean Dist Directory
echo "Cleaning dist/ directory..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 2. Copy Frontend Assets
echo "Copying frontend assets..."
cp -r "$FRONTEND_DIR"/* "$DIST_DIR"/

# 3. Generate Version Info
echo "Generating build info..."
cat <<EOF > "$DIST_DIR/build_info.json"
{
  "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "1.0.0",
  "environment": "production"
}
EOF

# 4. Success Message
echo ""
echo "✅ Build Complete!"
echo "Artifacts are ready in: $DIST_DIR"
echo "You can test by opening: $DIST_DIR/index.html"
echo "=============================="
