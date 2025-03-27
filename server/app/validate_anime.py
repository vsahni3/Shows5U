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
                    # print(data)
                    if data['data']:
                        anime = data['data'][0]
                        return {
                            'title': anime['title'],
                            'description': anime['synopsis'],
                            'genres': [genre['name'] for genre in anime['genres']],
                            'year': anime.get('year'),
                            'image_url': anime['images']['jpg']['image_url'],
                            'url': anime['url']
                        }
                #     print(data)
                # print(response)
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
                    # print(data)
                    if 'data' in data and 'Media' in data['data']:
                        anime = data['data']['Media']
                        return {
                            'title': anime['title']['romaji'],
                            'description': anime['description'],
                            'genres': anime['genres'],
                            'year': anime['startDate']['year'],
                            'image_url': anime['coverImage']['large'],
                            'url': anime['siteUrl']
                        }
                #     print(data)
                # print(response)
     
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
                    # print(data)
                    if data['data']:
                        anime = data['data'][0]['attributes']
                        return {
                            'title': anime['canonicalTitle'],
                            'description': anime['synopsis'],
                            'genres': [],  
                            'year': anime.get('startDate')[:4],
                            'image_url': anime['posterImage']['original'],
                            'url': f"https://kitsu.io/anime/{data['data'][0]['id']}"
                        }
                #     print(data)
                # print(response)
        return None
    
    @staticmethod
    async def search_find_my_anime(anime_title):
        """Search for anime using the find-my-anime API asynchronously."""
        url = 'https://find-my-anime.dtimur.de/api'
        params = {
            'query': anime_title,
            'provider': 'Kitsu',
            'includeAdult': 'true',
            'collectionConsent': 'true'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        anime = data[0]  # taking the first result

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
    async def validate(title):
        """Fetch anime details asynchronously and return the first valid result."""

        tasks = {
            asyncio.create_task(ValidateAnime.search_anilist(title)): "anilist",
            asyncio.create_task(ValidateAnime.search_jikan(title)): "jikan",
        }
        # see if caching gives enougb results without kitsu
        try:
            for future in asyncio.as_completed(tasks):
                result = await future
                if result:  
                    return result
            return await ValidateAnime.search_kitsu(title)
        except Exception as e:
            print(f"Error fetching from {title}: {e}") 
        
    
        # try:
        #     # searcj kitsu doesn't have genres, cant check hentai
        #     for f in [ValidateAnime.search_jikan, ValidateAnime.search_anilist, ValidateAnime.search_kitsu]:
        #         response = await f(title)
        #         if response and 'Hentai' not in response['genres']:
        #             return response
        # except Exception as e:
        #     print(f"Error {e}") 
            


# # Example Usage
if __name__ == "__main__":
    anime_title = 'Horimiya -piece-'
    anime_info = asyncio.run(ValidateAnime.validate(anime_title))
    print(anime_info['genres'])
    # if anime_info:
    #     print(f"Title: {anime_info['title']}")
    #     print(f"Description: {anime_info['description']}")
    #     print(f"Genres: {', '.join(anime_info['genres'])}")
    #     print(f"Year: {anime_info['year']}")
    #     print(f"Image URL: {anime_info['image_url']}")  # ✅ Prints the anime image URL
    #     print(f"More Info: {anime_info['url']}")
    # else:
    #     print("Anime not found.")
