#!/bin/bash
# install.sh — Quaker Display installer for Inky Impression 7.3"
# Run with: bash install.sh

set -e

INSTALL_DIR="/home/pi/quaker-display"
SERVICE_NAME="quaker-display"
VENV_DIR="$INSTALL_DIR/venv"

echo ""
echo "========================================"
echo "  Quaker Display — Installer"
echo "========================================"
echo ""

# --- Check running as pi or with sudo ---
if [ "$EUID" -eq 0 ]; then
  echo "Do not run this script as root. Run as the pi user: bash install.sh"
  exit 1
fi

# --- Copy files to install directory ---
echo "[1/6] Copying files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/quotes/images"

cp quaker_display.py "$INSTALL_DIR/"

# Only copy sample quotes if no quotes.json exists yet
if [ ! -f "$INSTALL_DIR/quotes/quotes.json" ]; then
  cp quotes/quotes.json "$INSTALL_DIR/quotes/quotes.json"
  echo "      Sample quotes.json installed."
else
  echo "      quotes.json already exists — skipping to preserve your quotes."
fi

echo "      Drop your images into: $INSTALL_DIR/quotes/images/"
echo ""

# --- Create virtual environment ---
echo "[2/6] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
echo ""

# --- Install Python dependencies ---
echo "[3/6] Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install "inky[rpi]" pillow --quiet
echo ""

# --- Install systemd service and timer ---
echo "[4/6] Installing systemd service and timer..."
sudo cp systemd/quaker-display.service /etc/systemd/system/
sudo cp systemd/quaker-display.timer /etc/systemd/system/
echo ""

# --- Reload systemd and enable ---
echo "[5/6] Enabling and starting timer..."
sudo systemctl daemon-reload
sudo systemctl enable quaker-display.timer
sudo systemctl start quaker-display.timer
echo ""

# --- Run once immediately ---
echo "[6/6] Running display update now..."
sudo systemctl start quaker-display.service
echo ""

echo "========================================"
echo "  Installation complete."
echo ""
echo "  Quotes file:  $INSTALL_DIR/quotes/quotes.json"
echo "  Images folder: $INSTALL_DIR/quotes/images/"
echo ""
echo "  The display will refresh every hour."
echo "  Check status with:"
echo "    sudo systemctl status quaker-display.timer"
echo "    sudo journalctl -u quaker-display.service"
echo "========================================"
echo ""
