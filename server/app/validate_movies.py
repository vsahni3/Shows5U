import requests
import os
import aiohttp
from app.validate import Validator
import asyncio
from dotenv import load_dotenv
load_dotenv()

class ValidateMovies(Validator):
    
    omdb_api_key = os.getenv('OMDB_API_KEY')
    tmdb_api_key = os.getenv('TMDB_API_KEY')
    # same instance only 1 content type
    def __init__(self, content_type):
        self.content_type = content_type
        
    async def search_omdb(self, title):
        """Search for a movie or TV show in OMDb asynchronously."""
        url = f"http://www.omdbapi.com/?t={title}&type={self.content_type}&apikey={ValidateMovies.omdb_api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    if data.get("Response") == "True":
                        poster_url = data.get("Poster")
                        return {
                            "title": data["Title"],
                            "description": data["Plot"],
                            "genres": data["Genre"].split(", "),
                            "year": data.get("Year"),
                            "image_url": poster_url,
                            "url": f"https://www.imdb.com/title/{data['imdbID']}"
                        }
        return None

    async def search_tmdb(self, title):
        """Search for a movie or TV show in TMDb asynchronously."""
        media_type = "movie" if self.content_type == "movie" else "tv"
        url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={ValidateMovies.tmdb_api_key}&query={title}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["results"]:
                        result = data["results"][0]  # Take the first search result
                        poster_path = result.get("poster_path")
                        backdrop_path = result.get("backdrop_path")
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

                        return {
                            "title": result["title"] if media_type == "movie" else result["name"],
                            "description": result["overview"],
                            "genres": [],  # TMDb genres require a separate API call
                            "year": int(result.get("release_date")[:4]) if media_type == "movie" else int(result.get("first_air_date")[:4]),
                            "image_url": poster_url,
                            "url": f"https://www.themoviedb.org/{media_type}/{result['id']}"
                        }
        return None

    async def validate(self, title):
        """Fetch movie or TV show details from multiple sources and return the first available response."""

        # tasks = {
        #     asyncio.create_task(self.search_omdb(title)): "omdb",
        #     asyncio.create_task(self.search_tmdb(title)): "tmdb",
        # }
        
        # for future in asyncio.as_completed(tasks):
        #     try:
        #         result = await future
        #         if result:
        #             for task in tasks:
        #                 if not task.done():
        #                     task.cancel()
        #             return result 
        #     except Exception:
        #         print(f"Error fetching from {title}: {e}") 
        # need omdb first as it has genres
        try:
            response = await self.search_omdb(title)
            if response:
                return response
            response = await self.search_tmdb(title)
            return response
        except Exception as e:
            print(f"Error {e}") 



# # Example usage
if __name__ == '__main__':
    title = "The Notebook"  # Change this to a movie or TV show title
    content_type = "movie"  # Use "movie" or "series" (TV)
    validator = ValidateMovies(content_type)
    info = asyncio.run(validator.validate(title))

    if info:
        print(f"Title: {info['title']}")
        print(f"Description: {info['description']}")
        print(f"Genres: {', '.join(info['genres'])}")
        print(f"Year: {info['year']}")
        print(f"Image URL: {info['image_url']}")
        print(f"More Info: {info['url']}")
    else:
        print("No data found.")
