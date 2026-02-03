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
