import requests

def search_jikan(anime_title):
    """Search for anime in Jikan API (MyAnimeList) and include the image URL."""
    query = anime_title.replace(' ', '%20')
    url = f'https://api.jikan.moe/v4/anime?q={query}&limit=1'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            anime = data['data'][0]
            return {
                'title': anime.get('title'),
                'description': anime.get('synopsis'),
                'genres': [genre['name'] for genre in anime.get('genres', [])],
                'year': anime.get('year'),
                'image_url': anime.get('images', {}).get('jpg', {}).get('image_url'),  # ✅ Extract image
                'url': anime.get('url')
            }
    return None

def search_anilist(anime_title):
    """Search for anime in AniList API and include the image URL."""
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
                large  # ✅ Get high-quality image URL
            }
            siteUrl
        }
    }
    '''
    variables = {'search': anime_title}
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        data = response.json()
        anime = data['data']['Media']
        return {
            'title': anime['title']['romaji'],
            'description': anime['description'],
            'genres': anime['genres'],
            'year': anime['startDate']['year'],
            'image_url': anime.get('coverImage', {}).get('large'),  # ✅ Extract image URL
            'url': anime['siteUrl']
        }
    return None

def search_kitsu(anime_title):
    """Search for anime in Kitsu API and include the image URL."""
    query = anime_title.replace(' ', '%20')
    url = f'https://kitsu.io/api/edge/anime?filter[text]={query}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            anime = data['data'][0]['attributes']
            return {
                'title': anime.get('canonicalTitle'),
                'description': anime.get('synopsis'),
                'genres': [],  # Kitsu does not return genres in the same way
                'year': anime.get('startDate', '')[:4],
                'image_url': anime.get('posterImage', {}).get('original'),  # ✅ Extract image URL
                'url': f"https://kitsu.io/anime/{data['data'][0]['id']}"
            }
    return None

def get_anime_info(anime_title):
    """Fetch anime details from multiple sources, including image URLs."""
    info = search_jikan(anime_title)
    if not info:
        info = search_anilist(anime_title)
    if not info:
        info = search_kitsu(anime_title)
    return info

# Example Usage
anime_title = 'Fullmetal Alchemist: Brotherhood'
anime_info = get_anime_info(anime_title)

if anime_info:
    print(f"Title: {anime_info['title']}")
    print(f"Description: {anime_info['description']}")
    print(f"Genres: {', '.join(anime_info['genres'])}")
    print(f"Year: {anime_info['year']}")
    print(f"Image URL: {anime_info['image_url']}")  # ✅ Prints the anime image URL
    print(f"More Info: {anime_info['url']}")
else:
    print("Anime not found.")
