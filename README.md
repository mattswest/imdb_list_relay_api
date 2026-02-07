# IMDb List Relay API

A lightweight relay server designed to scrape IMDb movie lists and serve the data in a JSON format compatible with Radarr as a StevenLu Custom List.

## Features
- Scrapes IMDb lists using the `__NEXT_DATA__` JSON block for high reliability.
- Returns clean JSON with movie titles, years, IMDb IDs, and poster URLs.
- Built with FastAPI for high performance.
- Easy to run as a systemd service.

## API Endpoints

### `GET /list/{list_id}`
Returns the list of movies for the given IMDb list ID.
- **Example**: `GET /list/ls031657324`

### `GET /`
Health check endpoint.

## Adding to Radarr

You can use this relay to add IMDb lists to Radarr as a "StevenLu Custom" list.

1. In Radarr, navigate to **Settings** > **Lists**.
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

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/imdb_scraper_api.git
   cd imdb_scraper_api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```
   The server will start on port `9191`.

## Running as a Service (Linux)

A systemd service file `imdb-relay.service` is provided. To use it:

1. Edit the `User`, `WorkingDirectory`, and `ExecStart` paths in `imdb-relay.service` to match your environment.
2. Link or copy the service file:
   ```bash
   sudo ln -s /path/to/imdb-relay.service /etc/systemd/system/
   ```
3. Start and enable the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable imdb-relay
   sudo systemctl start imdb-relay
   ```

## Technologies Used
- **Python 3**
- **FastAPI**
- **BeautifulSoup4**
- **Requests**
- **Uvicorn**
