from app.validate_movies import ValidateMovies
from app.validate_anime import ValidateAnime

class ValidatorHandler:
    def __init__(self, content_type: str):
        if content_type == 'anime':
            self.validator = ValidateAnime()
        else:
            self.validator = ValidateMovies(content_type)
            
    def search(self, title):
        return self.validator.validate(title)

def validate_titles(content_type: str, titles: set[str]):
    validator_handler = ValidatorHandler(content_type)
    results = [result for title in titles if (result := validator_handler.search(title))]
    return results 