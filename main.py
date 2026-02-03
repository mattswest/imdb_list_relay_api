from fastapi import FastAPI, HTTPException
from scraper import scrape_imdb_list

app = FastAPI(title="IMDb List Relay API")

@app.get("/list/{list_id}")
async def get_list(list_id: str):
    """
    Scrapes an IMDb movie list and returns it in a format usable by Radarr.
    """
    try:
        movies = scrape_imdb_list(list_id)
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "IMDb List Relay API is running. Use /list/{list_id} to scrape a list."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9191)
