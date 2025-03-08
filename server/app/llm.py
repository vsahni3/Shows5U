from abc import ABC, abstractmethod
import cohere
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
# idea for implementing comments + rating
# good rating means find similar descriptions
# comment is isolated from anime, use it as an additional way to match anime descritpions


class LLMModel(ABC):
    
    def __init__(self, content_type):
        self.system_prompt = f"You are a {content_type} recommender system that gives ONLY COMMA separated {content_type} titles to the user AND NOTHING ELSE. For example: 'Naruto; One piece; Bleach'"
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
        message = f"Find the most relevant and mainstream semi-colon separated {self.content_type} titles matching the prompt: {prompt}. Output your answer in this EXACT format 'title1; title2; title3'"
        response = await self.client.chat(
            message=message,
            connectors=[{"id": "web-search"}],
            preamble=self.system_prompt,
            model=self.model,
            temperature=1.0
        )
        return response.text.strip()


class ModelHandler:
    
    def __init__(self, model_name: str, **kwargs):
        if model_name.lower() == "cohere":
            self.model = CohereModel(**kwargs)
        else:
            raise ValueError(f"Model '{model_name}' is not supported.")
    
    async def generate_multiple(self, prompt: str, n_calls: int = 5):
        coroutines = [self.model.generate(prompt) for _ in range(n_calls)]
        results = await asyncio.gather(*coroutines)
        cleaned_results = [set(result.split('; ')) for result in results]
        aggregated_results = set().union(*cleaned_results)
        return aggregated_results
        
def generate(prompt: str, content_type: str, model_name: str = 'cohere'):
    model = ModelHandler(model_name, content_type=content_type)
    result = asyncio.run(model.generate_multiple(prompt))
    return result

# ✅ Example usage
if __name__ == "__main__":
    
    model = ModelHandler("cohere", content_type='anime')
    
    
    # Generate text
    prompt = "female mc"
    result = asyncio.run(model.generate_multiple(prompt))
    
    print(result)
