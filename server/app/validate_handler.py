from app.validate_movies import ValidateMovies
from app.validate_anime import ValidateAnime
from app.redis import cache_results, get_cached_results_with_fallback, map_names, redis_client, clear_cache
from app.llm import generate
from app.constants import FORBIDDEN_GENRES, TO_AVOID
from app.utils import left_to_right_match
from time import sleep, time
# if caching memory  not enough, can always just czche genres and title for kitsu
import asyncio 

class ValidatorHandler:
    def __init__(self, content_type: str):
        self.content_type = content_type
        if self.content_type == 'anime':
            self.validator = ValidateAnime()
        else:
            self.validator = ValidateMovies(content_type)
    
    # dont want to change eevry validate method of diff classes for common processing
    async def validate_single(self, title: str, to_map: list):
        result = await self.validator.validate(title)
        if not result or len(set(result['genres']).intersection(FORBIDDEN_GENRES)) > 0 or result['title'] in TO_AVOID:
            return {}
        result = {k: ("" if v is None else v) for k, v in result.items()}
        if self.content_type == 'anime':
            result['title'] = result['title'].rstrip('!')
            actual_title = result['title']
            # japanese vs english
            if left_to_right_match(title, actual_title) < 0.5:
                to_map.append((title, actual_title))
        return result
                
                
            
    async def validate_multiple(self, titles: set[str]):
        to_map = []
        async with redis_client() as r:
            cached_dict = await get_cached_results_with_fallback(r, list(titles), self.content_type)

        cached_titles = set(cached_dict.keys())
        cached_results = list(cached_dict.values())
        titles -= cached_titles
        coroutines = [self.validate_single(title, to_map) for title in titles]
        results = await asyncio.gather(*coroutines)
        results = list(filter(bool, results))
        final_results = results + cached_results
        # make unique by setting equal to dict keys
        dict_results = {result['title'].lower(): result for result in final_results if result}
        final_results = list(dict_results.values())
        return final_results, to_map, results
        

def validate_titles(content_type: str, titles: set[str]):
    validator_handler = ValidatorHandler(content_type)
    results = asyncio.run(validator_handler.validate_multiple(titles))
    return results 

if __name__ == "__main__":


    from time import time, sleep
    start = time()
    
    
    a = validate_titles('anime', set())

    # sleep(10)

