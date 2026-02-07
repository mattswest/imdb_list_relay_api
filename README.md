# IMDb List Relay API

A lightweight relay server designed to scrape IMDb movie lists and serve the data in a JSON format compatible with the "StevenLu Custom" list option in Radarr.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mattswest/imdb_list_relay_api
   cd imdb_list_relay_api
   ```

2. **Run the installer**:
   ```bash
   ./install.sh
   ```
   This script will:
   - Create a Python virtual environment.
   - Install all dependencies.
   - Configure and install the systemd service automatically.

3. **Verify**:
   Check that the service is running:
   ```bash
   sudo systemctl status imdb-relay
   ```
   The server listens on port `9191` by default.

## Adding to Radarr

You can use this relay to add IMDb lists to Radarr as a "StevenLu Custom" list.

1. In Radarr, navigate to **Settings** > **Import Lists**.
2. Click the **+** button to add a new list.
3. Select **StevenLu Custom** from the available options.
4. Configure the following:
   - **Name**: A name for your list (e.g., "IMDb Sci-Fi").
   - **List URL**: `http://<YOUR_IP>:9191/list/<LIST_ID>`
     - Replace `<YOUR_IP>` with the IP or hostname of the server running this relay.
     - Replace `<LIST_ID>` with the IMDb list ID (e.g., `ls031657324`).
5. (Optional) Configure other settings like **Minimum Availability** or **Root Folder**.
6. Click **Test** to ensure Radarr can reach the relay and parse the list.
7. Click **Save**.

## Technologies Used
- **Python 3**
- **FastAPI**
- **BeautifulSoup4**
- **Requests**
- **Uvicorn**
