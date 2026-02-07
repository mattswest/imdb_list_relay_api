#!/bin/bash

set -e

# Get current user and directory
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python3"

echo "=== IMDb List Relay API Installer ==="

# 0. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[-] Error: python3 is not installed."
    exit 1
fi

echo "Detected User: $CURRENT_USER"
echo "Detected Directory: $PROJECT_DIR"

# 1. Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[*] Virtual environment already exists."
fi

# 2. Install Dependencies
echo "[+] Installing dependencies..."
"$PYTHON_EXEC" -m pip install --upgrade pip > /dev/null
"$PYTHON_EXEC" -m pip install -r requirements.txt

# 3. Configure Service File
echo "[+] Configuring systemd service file..."
SERVICE_FILE="imdb-relay.service"

# Use sed to replace User, WorkingDirectory, and ExecStart
# We use | as delimiter to avoid conflicts with slashes in paths
sed -i "s|^User=.*|User=$CURRENT_USER|" "$SERVICE_FILE"
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|" "$SERVICE_FILE"
sed -i "s|^ExecStart=.*|ExecStart=$PYTHON_EXEC main.py|" "$SERVICE_FILE"

echo "[*] Service file updated with:"
grep -E "User=|WorkingDirectory=|ExecStart=" "$SERVICE_FILE"

# 4. Install Service
echo "[+] Installing systemd service (requires sudo)..."
if sudo cp "$SERVICE_FILE" /etc/systemd/system/; then
    sudo systemctl daemon-reload
    sudo systemctl enable imdb-relay
    sudo systemctl restart imdb-relay
    echo "[+] Installation complete! Service is running."
    echo ""
    echo "Check status with: sudo systemctl status imdb-relay"
else
    echo "[-] Failed to install service. Please run script with appropriate permissions or check sudo access."
    exit 1
fi
