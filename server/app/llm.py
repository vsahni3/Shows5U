from abc import ABC, abstractmethod
import cohere
import os
import asyncio
from random import randint
from dotenv import load_dotenv
from app.redis import get_titles, redis_client
load_dotenv()
# idea for implementing comments + rating
# good rating means find similar descriptions
# comment is isolated from anime, use it as an additional way to match anime descritpions


class LLMModel(ABC):
    
    def __init__(self, content_type):
        self.system_prompt = f"You are a {content_type} recommender AI that can browse the internet and gives ONLY SEMI-COLON separated {content_type} titles to the user AND NOTHING ELSE. For example: 'Naruto; One piece; Bleach'"
        self.content_type = content_type
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass


class CohereModel(LLMModel):

    def __init__(self, content_type: str, model: str = "command-r7b-12-2024"):
        super().__init__(content_type)
        self.model = model
        api_key = os.getenv("COHERE_API_KEY")
        self.client = cohere.AsyncClient(api_key)

    async def generate(self, prompt: str) -> str:
        random_seed = randint(0, 1000)
        instructions = f"Recommend at least 10 of the most popular and mainstream semi-colon separated {self.content_type} titles accurately matching the prompt: {self.content_type} like {prompt}. Don't give explicit content"
        message = (
            "## Instructions\n"
            f"{instructions}\n"
            f"Random seed: {random_seed}\n"
            "## Output Format\n"
            "Provide the titles separated by semicolons, like so: 'title1; title2; title3'"
        )
        retries = 5
        for i in range(retries):
            try:
                response = await self.client.chat(
                    message=message,
                    connectors=[{"id": "web-search"}],
                    model=self.model,
                    preamble=self.system_prompt,
                    temperature=0.9,
                    p=0.9
                )
                return response.text.strip().lower()
            except Exception as e:
                print(f'Error: {e}')
        raise ValueError
            
        


class ModelHandler:
    
    def __init__(self, model_name: str, content_type: str, **kwargs):
        self.content_type = content_type
        if model_name.lower() == "cohere":
            self.model = CohereModel(content_type, **kwargs)
        else:
            raise ValueError(f"Model '{model_name}' is not supported.")
    
    async def generate_multiple(self, prompt: str, n_calls: int = 10):
        async with redis_client() as r:
            cached_titles = await get_titles(r, prompt, self.content_type)
        if cached_titles:
            return cached_titles
        coroutines = [self.model.generate(prompt) for _ in range(n_calls)]
        results = await asyncio.gather(*coroutines)
        cleaned_results = [set(result.split('; ')) for result in results]
        aggregated_results = set().union(*cleaned_results)
        return aggregated_results
        
def generate(prompt: str, content_type: str, model_name: str = 'cohere'):
    model = ModelHandler(model_name, content_type)
    result = asyncio.run(model.generate_multiple(prompt))
    return result

# ✅ Example usage
if __name__ == "__main__":
    
    model = ModelHandler("cohere", content_type='anime')
    
    
    # Generate text
    prompt = "like solo leveling"
    result = asyncio.run(model.generate_multiple(prompt))
    
    print(result)
    



