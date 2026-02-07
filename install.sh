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

# 3. Create Service File
echo "[+] Creating systemd service file..."
SERVICE_FILE="imdb-relay.service"

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=IMDb List Relay API for Radarr
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_EXEC main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "[*] Service file created."

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
