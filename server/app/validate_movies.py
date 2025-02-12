import requests
import os
from validate import Validator
from dotenv import load_dotenv
load_dotenv()

class ValidateMovies(Validator):
    
    omdb_api_key = os.getenv('OMDB_API_KEY')
    tmdb_api_key = os.getenv('TMDB_API_KEY')
    # same instance only 1 content type
    def __init__(self, content_type):
        self.content_type = content_type
        
    def search_omdb(self, title, content_type):
        """Search for a movie or TV show in OMDb and return details including image URL."""
        url = f"http://www.omdbapi.com/?t={title}&type={self.content_type}&apikey={ValidateMovies.omdb_api_key}"

        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return {
                    "title": data.get("Title"),
                    "description": data.get("Plot"),
                    "genres": data.get("Genre", "").split(", "),
                    "year": data.get("Year"),
                    "poster_url": data.get("Poster"),  
                    "url": f"https://www.imdb.com/title/{data.get('imdbID')}"
                }
        return None

    def search_tmdb(self, title):
        """Search for a movie or TV show in TMDb and return details including image URL."""
        media_type = "movie" if self.content_type == "movie" else "tv"
        url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={ValidateMovies.tmdb_api_key}&query={title}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                result = data["results"][0]  # Take the first search result
                poster_path = result.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None  # ✅ Construct full image URL

                return {
                    "title": result.get("title") if media_type == "movie" else result.get("name"),
                    "description": result.get("overview"),
                    "genres": ["Unknown"],  # TMDb genres require a separate API call
                    "year": result.get("release_date", "")[:4] if media_type == "movie" else result.get("first_air_date", "")[:4],
                    "poster_url": poster_url,  # ✅ Image URL
                    "url": f"https://www.themoviedb.org/{media_type}/{result.get('id')}"
                }
        return None

    def search(self, title):
        """Fetch movie or TV show details from multiple sources, including images."""
        info = self.search_omdb(title, content_type)
        if not info:
            info = self.search_tmdb(title, content_type)
        return info

# Example usage
title = "Inception"  # Change this to a movie or TV show title
content_type = "movie"  # Use "movie" or "series" (TV)

info = get_movie_or_tv_info(title, content_type)

if info:
    print(f"Title: {info['title']}")
    print(f"Description: {info['description']}")
    print(f"Genres: {', '.join(info['genres'])}")
    print(f"Year: {info['year']}")
    print(f"Poster URL: {info['poster_url']}")
    print(f"More Info: {info['url']}")
else:
    print("No data found.")
