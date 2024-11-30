import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating
from model.artist import Artist
from service.itunes import search_artist
import requests

"""
This is the main entry point for the application.

Here we configure app level services and routes, 
like logging and the template engine used to render the HTML pages.

We also initialize our AlbumService port, which is configured with
two adapters:
- FileCacheAlbumService, which uses the file system to cache albums that have been downloaded
- iTunesAlbumService, which uses the iTunes API to download new albums
"""

# Configure logging to show info level and above to the console, using our custom format
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(name)s - %(message)s')

# Configure the Jinja2 template engine
templates = templating.Jinja2Templates(directory="templates")

# Configure the FastAPI app to serve the API and the home page
app = FastAPI()


# Serves the home page at / using the Jinja2 template engine
@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# API route to get a list of albums for an artist
@app.get("/artist/{name}")
def get_artist(name: str):
    if match := re.search(r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()):
        artist_name = " ".join(match.groups())
        # should we pass in the limit in the querystring?
        artist = search_artist(artist_name, 3)
        # print(artist)
        return artist
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid artist name: {name}")

# Here we can add more API routes for other functionality, like:
# - API route to get a list of albums for a genre
# - API route to get a list of albums for a year
# - API route to get a list of albums for a decade

def fetch_album_data(artist_name, album_name):
    base_url = 'https://itunes.apple.com/search'
    params = {
        'term': f'{artist_name} {album_name}',
        'media': 'music',
        'entity': 'album',
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]
    return None

from PIL import Image
import requests
from io import BytesIO

def display_album_artwork(artwork_url):
    response = requests.get(artwork_url)
    if response.status_code == 200:
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.show()

def main():
    artist_name = input("Enter the artist's name: ")
    album_name = input("Enter the album's name: ")
    album_data = fetch_album_data(artist_name, album_name)
    if album_data:
        artwork_url = album_data.get('artworkUrl100')
        if artwork_url:
            display_album_artwork(artwork_url)
        else:
            print("Artwork not found.")
    else:
        print("Album not found.")

if __name__ == '__main__':
    main()
