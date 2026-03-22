#!/bin/bash

# OpenClaw Memory V51 Plugin Installer
# Supports: macOS, Linux, WSL

set -e

echo "========================================"
echo "OpenClaw Memory V51 Plugin Installer"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js not found!${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}[ERROR] npm not found!${NC}"
    echo "Please install npm (comes with Node.js)"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} npm found: $(npm --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}[WARN] Python 3 not found, skipping database initialization${NC}"
    PYTHON_AVAILABLE=false
else
    echo -e "${GREEN}[OK]${NC} Python found: $(python3 --version)"
    PYTHON_AVAILABLE=true
fi

echo ""
echo "[INFO] Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] npm install failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[OK]${NC} Dependencies installed successfully!"
echo ""

# Compile TypeScript
echo "[INFO] Compiling TypeScript..."
npm run build

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARN] TypeScript compilation failed!${NC}"
    echo "Trying to continue with existing build..."
else
    echo -e "${GREEN}[OK]${NC} Build complete!"
fi

echo ""

# Initialize database (if Python available)
if [ "$PYTHON_AVAILABLE" = true ]; then
    echo "[INFO] Initializing database..."
    python3 -c "from memory_core_v2 import init_db; init_db(); print('[OK] Database initialized')"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit ~/.openclaw/openclaw.json"
echo "   (or C:\Users\user\.openclaw\openclaw.json on Windows)"
echo "2. Add \"memory-v51\" to plugins.allow"
echo "3. Enable in plugins.entries.memory-v51"
echo "4. Run: openclaw gateway restart"
echo ""
