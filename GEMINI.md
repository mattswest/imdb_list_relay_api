# Project Overview: IMDb List Relay API

This project is a relay server designed to scrape IMDb movie lists and serve the data in a JSON format compatible with Radarr. It extracts key movie details including title, release year, IMDb ID, and poster URL.

## Main Technologies
- **Python 3**: Core programming language.
- **FastAPI**: Web framework for building the API.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **BeautifulSoup4**: For parsing IMDb's HTML.
- **Requests**: For fetching webpage content.

## Architecture
- `scraper.py`: Contains the logic to fetch IMDb list pages, extract the embedded `__NEXT_DATA__` JSON block, and parse it into a standardized movie list.
- `main.py`: The entry point that defines the API endpoints using FastAPI.
- `imdb-relay.service`: A systemd unit file for managing the application as a background service.

## Building and Running

### Prerequisites
- Python installed (configured with Miniconda in this environment).
- Dependencies listed in `requirements.txt`.

### Installation
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
python main.py
```
The server defaults to port **9191**.

### Running as a Service
The project is configured to run as a systemd service:
- **Start**: `sudo systemctl start imdb-relay`
- **Stop**: `sudo systemctl stop imdb-relay`
- **Status**: `sudo systemctl status imdb-relay`
- **Logs**: `journalctl -u imdb-relay -f`

## API Endpoints
- `GET /list/{list_id}`: Scrapes the specified IMDb list ID (e.g., `ls031657324`) and returns a JSON list of movies.
- `GET /`: Health check endpoint.

## Development Conventions
- **Data Extraction**: Prefers parsing the `__NEXT_DATA__` script tag over raw HTML selectors for better reliability.
- **Error Handling**: Implements checks for missing fields (poster, year) to prevent 500 errors.
- **Environment**: Configured to run under user `matt` in `/home/matt/gemini-projects/imdb_scraper_api`.
