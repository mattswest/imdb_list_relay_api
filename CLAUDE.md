# Project Overview: IMDb List Relay API

This project is a relay server that retrieves IMDb movie lists through IMDb's GraphQL endpoint and serves the data in a JSON format compatible with Radarr. It extracts title, release year, IMDb ID, and poster URL while preserving the list's order.

## Main Technologies
- **Python 3**: Core programming language.
- **FastAPI**: Web framework for building the API.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **Requests**: For calling IMDb's GraphQL endpoint.
- **Pytest**: For focused offline regression tests.

## Architecture
- `scraper.py`: Posts to `https://api.graphql.imdb.com/`, follows `list.items` cursor pagination, validates every page and item, and returns a standardized movie list.
- `main.py`: Defines the FastAPI endpoints and maintains a 24-hour JSON cache. Cache entries are replaced atomically only after a complete successful scrape.
- `tests/test_scraper.py`: Covers pagination, ordering, output shape, nullable metadata, and upstream failure handling without relying on live IMDb responses.
- `tests/test_main.py`: Covers successful and failed cache behavior.
- `imdb-relay.service`: A systemd unit file for managing the application as a background service.

## Building and Running

### Prerequisites
- Python 3 installed.
- Dependencies listed in `requirements.txt`.

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
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
- `GET /list/{list_id}`: Retrieves the specified IMDb list ID (e.g., `ls031657324`) and returns a JSON list of movies.
- `GET /`: Health check endpoint.

## Development Conventions
- **Data Extraction**: Use the unauthenticated IMDb GraphQL endpoint with `Origin: https://www.imdb.com`; do not implement CAPTCHA or WAF bypasses.
- **Pagination**: Fetch every page through `pageInfo.hasNextPage` and `endCursor`, preserving edge order. Treat missing or repeated cursors as upstream failures.
- **Return Shape**: Preserve `scrape_imdb_list(list_id)` output as a list of `{"title", "year", "imdb_id", "poster_url"}` dictionaries. Missing year and poster values are `None`.
- **Error Handling**: Raise clear `IMDbScraperError` exceptions for HTTP, JSON, GraphQL, pagination, and required metadata failures. Never silently return partial results.
- **Caching**: Cache only complete successful results. Failed or partial scrapes must not replace an existing cache entry.
- **Testing**: Run focused tests with `python3 -m pytest -q`. Live verification should isolate or bypass stale cache entries.
- **Environment**: Configured to run under user `matt` in `/home/matt/gemini-projects/imdb_scraper_api`.
