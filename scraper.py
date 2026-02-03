import json
import requests
from bs4 import BeautifulSoup

def scrape_imdb_list(list_id: str):
    url = f"https://www.imdb.com/list/{list_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
        raise Exception("Could not find __NEXT_DATA__ script tag")
        
    data = json.loads(script_tag.string)
    
    # Path to items: props -> pageProps -> mainColumnData -> list -> titleListItemSearch -> edges
    try:
        items_data = data['props']['pageProps']['mainColumnData']['list']['titleListItemSearch']['edges']
    except KeyError:
        raise Exception("Failed to parse IMDb JSON structure")
        
    movies = []
    for edge in items_data:
        if not edge:
            continue
        item = edge.get('listItem')
        if not item:
            continue
            
        title_data = item.get('titleText')
        if not title_data:
            continue
        title = title_data.get('text')
        
        imdb_id = item.get('id')
        
        year_data = item.get('releaseYear')
        year = year_data.get('year') if year_data else None
        
        primary_image = item.get('primaryImage')
        poster_url = primary_image.get('url') if primary_image else None
        
        movies.append({
            "title": title,
            "year": year,
            "imdb_id": imdb_id,
            "poster_url": poster_url
        })
        
    return movies

if __name__ == "__main__":
    # Test with example list
    import pprint
    try:
        results = scrape_imdb_list("ls031657324")
        pprint.pprint(results[:2])
    except Exception as e:
        print(f"Error: {e}")
