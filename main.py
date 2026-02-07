import json
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from scraper import scrape_imdb_list

app = FastAPI(title="IMDb List Relay API")

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_DURATION = 86400  # 24 hours in seconds

@app.get("/list/{list_id}")
async def get_list(list_id: str):
    """
    Scrapes an IMDb movie list and returns it in a format usable by Radarr.
    Results are cached for 24 hours.
    """
    cache_file = CACHE_DIR / f"{list_id}.json"

    # Check cache
    if cache_file.exists():
        last_modified = cache_file.stat().st_mtime
        if time.time() - last_modified < CACHE_DURATION:
            try:
                with open(cache_file, "r") as f:
                    print(f"Serving {list_id} from cache.")
                    return json.load(f)
            except Exception as e:
                print(f"Error reading cache for {list_id}: {e}")

    try:
        movies = scrape_imdb_list(list_id)
        
        # Save to cache
        try:
            with open(cache_file, "w") as f:
                json.dump(movies, f)
        except Exception as e:
            print(f"Failed to write cache for {list_id}: {e}")
            
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "IMDb List Relay API is running. Use /list/{list_id} to scrape a list."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9191)