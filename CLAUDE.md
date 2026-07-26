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
- `install-sudoers.sh`: Installs a sudoers drop-in granting `matt` passwordless restart of this one unit. Every value is hardcoded; it refuses to run as non-root and validates with `visudo` before installing.
- `requirements-dev.txt`: Test-only dependencies (`pytest`, `httpx`), kept separate so the service installs nothing it does not need at runtime.

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
The project is configured to run as a systemd service (`User=matt`, `Restart=always`, `RestartSec=5`):
- **Start**: `sudo systemctl start imdb-relay`
- **Stop**: `sudo systemctl stop imdb-relay`
- **Restart**: `sudo -n systemctl restart imdb-relay`
- **Status**: `sudo systemctl status imdb-relay`
- **Logs**: `journalctl -u imdb-relay -f`

### Deploying Code Changes
The service imports `main.py` once at startup, so **source edits have no effect until the unit is restarted**. A stale process keeps serving old behaviour and old error strings long after the code is fixed; this previously surfaced as Radarr receiving HTTP 500 `Could not find __NEXT_DATA__ script tag` from a months-old process while the repository already contained the GraphQL fix.
```bash
sudo -n systemctl restart imdb-relay
```
Always confirm the process was actually replaced rather than assuming the restart worked:
```bash
systemctl show imdb-relay -p MainPID -p ActiveEnterTimestamp
```

### Passwordless Restart
`sudo ./install-sudoers.sh` installs `/etc/sudoers.d/imdb-relay-restart`, granting `matt` NOPASSWD rights to restart this unit only (both the `imdb-relay` and `imdb-relay.service` spellings, because sudo matches the command line literally).

When verifying that rule, run `sudo -k` first: a cached sudo credential makes any `sudo -n` check succeed regardless of the rule. Do not use `sudo -l <command>` as proof, since it reports only whether a command is permitted, not whether it is passwordless.

## API Endpoints
- `GET /list/{list_id}`: Retrieves the specified IMDb list ID (e.g., `ls031657324`) and returns a JSON list of movies.
- `GET /`: Health check endpoint.

## Development Conventions
- **Data Extraction**: Use the unauthenticated IMDb GraphQL endpoint with `Origin: https://www.imdb.com`; do not implement CAPTCHA or WAF bypasses.
- **Pagination**: Fetch every page through `pageInfo.hasNextPage` and `endCursor`, preserving edge order. Treat missing or repeated cursors as upstream failures.
- **Return Shape**: Preserve `scrape_imdb_list(list_id)` output as a list of `{"title", "year", "imdb_id", "poster_url"}` dictionaries. Missing year and poster values are `None`.
- **Error Handling**: Raise clear `IMDbScraperError` exceptions for HTTP, JSON, GraphQL, pagination, and required metadata failures. Never silently return partial results.
- **Caching**: Cache only complete successful results. Failed or partial scrapes must not replace an existing cache entry.
- **Testing**: The `.venv` created by the installer holds runtime dependencies only, so `python3 -m pytest` fails there with `No module named pytest`. Install the test extras once with `.venv/bin/pip install -r requirements-dev.txt`, then run `.venv/bin/python -m pytest -q`. Live verification should isolate or bypass stale cache entries.
- **Environment**: Configured to run under user `matt` in `/home/matt/gemini-projects/imdb_scraper_api`.
