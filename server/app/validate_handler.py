from app.validate_movies import ValidateMovies
from app.validate_anime import ValidateAnime
import asyncio 

class ValidatorHandler:
    def __init__(self, content_type: str):
        if content_type == 'anime':
            self.validator = ValidateAnime()
        else:
            self.validator = ValidateMovies(content_type)
            
    async def validate_multiple(self, titles: set[str]):
        coroutines = [self.validator.validate(title) for title in titles]
        results = await asyncio.gather(*coroutines)
        results = list(filter(lambda result: bool(result), results))
        # make unique by setting equal to dict keys
        dict_results = {result['title']: result for result in results}
        results = list(dict_results.values())
        return results
        

def validate_titles(content_type: str, titles: set[str]):
    validator_handler = ValidatorHandler(content_type)
    results = asyncio.run(validator_handler.validate_multiple(titles))
    return results 