#!/bin/bash
# install.sh — Quaker Display installer for Inky Impression 7.3"
# Run with: bash install.sh from inside the repo directory

set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$INSTALL_DIR/venv"

echo ""
echo "========================================"
echo "  Quaker Display — Installer"
echo "========================================"
echo ""

# --- Check not running as root ---
if [ "$EUID" -eq 0 ]; then
  echo "Do not run this script as root. Run as your normal user: bash install.sh"
  exit 1
fi

echo "[1/5] Setting up directories..."
mkdir -p "$INSTALL_DIR/quotes/images"
if [ ! -f "$INSTALL_DIR/quotes/quotes.json" ]; then
  echo "      No quotes.json found — please add one to $INSTALL_DIR/quotes/"
fi
echo "      Install directory: $INSTALL_DIR"
echo ""

# --- Create virtual environment ---
echo "[2/5] Creating Python virtual environment..."
rm -rf "$VENV_DIR"
python3 -m venv "$VENV_DIR"
echo ""

# --- Install Python dependencies ---
echo "[3/5] Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install inky pillow gpiozero --quiet
echo ""

# --- Install systemd files ---
echo "[4/5] Installing systemd service and timer..."
sed "s|\$USER|$USER|g; s|\$INSTALL_DIR|$INSTALL_DIR|g" \
  "$INSTALL_DIR/systemd/quaker-display.service" | sudo tee /etc/systemd/system/quaker-display.service > /dev/null
sudo cp "$INSTALL_DIR/systemd/quaker-refresh.service" /etc/systemd/system/
sudo cp "$INSTALL_DIR/systemd/quaker-display.timer" /etc/systemd/system/
echo ""

# --- Reload systemd and enable ---
echo "[5/5] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable quaker-display.service
sudo systemctl enable quaker-display.timer
sudo systemctl restart quaker-display.service
sudo systemctl start quaker-display.timer
echo ""

echo "========================================"
echo "  Installation complete."
echo ""
echo "  Quotes file:   $INSTALL_DIR/quotes/quotes.json"
echo "  Images folder: $INSTALL_DIR/quotes/images/"
echo ""
echo "  Buttons A/B/C/D refresh the display immediately."
echo "  Display also refreshes every 6 hours automatically."
echo ""
echo "  Check status:  sudo systemctl status quaker-display.service"
echo "  View logs:     sudo journalctl -u quaker-display.service -f"
echo "  Manual refresh: sudo systemctl kill --signal=SIGUSR1 quaker-display.service"
echo "========================================"
echo ""