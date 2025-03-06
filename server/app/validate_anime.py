import aiohttp
import asyncio
from app.validate import Validator

class ValidateAnime(Validator):
    
    @staticmethod
    async def search_jikan(anime_title):
        """Search for anime in Jikan API asynchronously."""
        query = anime_title.replace(' ', '%20')
        url = f'https://api.jikan.moe/v4/anime?q={query}&limit=1'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        anime = data['data'][0]
                        return {
                            'title': anime.get('title'),
                            'description': anime.get('synopsis'),
                            'genres': [genre['name'] for genre in anime.get('genres', [])],
                            'year': anime.get('year'),
                            'image_url': anime.get('images', {}).get('jpg', {}).get('image_url'),
                            'url': anime.get('url')
                        }
        return None

    @staticmethod
    async def search_anilist(anime_title):
        """Search for anime in AniList API asynchronously."""
        query = '''
        query ($search: String) {
            Media (search: $search, type: ANIME) {
                title {
                    romaji
                }
                description
                genres
                startDate {
                    year
                }
                coverImage {
                    large  
                }
                siteUrl
            }
        }
        '''
        variables = {'search': anime_title}
        url = 'https://graphql.anilist.co'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': query, 'variables': variables}) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and 'Media' in data['data']:
                        anime = data['data']['Media']
                        return {
                            'title': anime['title']['romaji'],
                            'description': anime['description'],
                            'genres': anime['genres'],
                            'year': anime['startDate']['year'],
                            'image_url': anime.get('coverImage', {}).get('large'),
                            'url': anime['siteUrl']
                        }
        return None

    @staticmethod
    async def search_kitsu(anime_title):
        """Search for anime in Kitsu API asynchronously."""
        query = anime_title.replace(' ', '%20')
        url = f'https://kitsu.io/api/edge/anime?filter[text]={query}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        anime = data['data'][0]['attributes']
                        return {
                            'title': anime.get('canonicalTitle'),
                            'description': anime.get('synopsis'),
                            'genres': [],  
                            'year': anime.get('startDate', '')[:4],
                            'image_url': anime.get('posterImage', {}).get('original'),
                            'url': f"https://kitsu.io/anime/{data['data'][0]['id']}"
                        }
        return None
    @staticmethod
    async def validate(title):
        """Fetch anime details asynchronously and return the first valid result."""

        tasks = {
            asyncio.create_task(ValidateAnime.search_jikan(title)): "Jikan",
            asyncio.create_task(ValidateAnime.search_anilist(title)): "AniList",
            asyncio.create_task(ValidateAnime.search_kitsu(title)): "Kitsu"
        }

        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                if result:  
                    for task in tasks:
                        if not task.done():
                            task.cancel()  
                    return result
            except Exception as e:
                print(f"Error fetching from {title}: {e}") 

        return None  # Return None if all sources failed

# # Example Usage
if __name__ == "__main__":
    anime_title = 'Fullmetal Alchemist: Brotherhood'
    anime_info = asyncio.run(ValidateAnime.validate(anime_title))
    if anime_info:
        print(f"Title: {anime_info['title']}")
        print(f"Description: {anime_info['description']}")
        print(f"Genres: {', '.join(anime_info['genres'])}")
        print(f"Year: {anime_info['year']}")
        print(f"Image URL: {anime_info['image_url']}")  # ✅ Prints the anime image URL
        print(f"More Info: {anime_info['url']}")
    else:
        print("Anime not found.")
