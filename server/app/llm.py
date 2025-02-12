from abc import ABC, abstractmethod
import cohere
import os
from dotenv import load_dotenv
load_dotenv()
# idea for implementing comments + rating
# good rating means find similar descriptions
# comment is isolated from anime, use it as an additional way to match anime descritpions


class LLMModel(ABC):
    
    def __init__(self, content_type):
        self.system_prompt = f'You are a {content_type} recommender system that gives ONLY COMMA separated {content_type} titles to the user AND NOTHING ELSE. For example: <Naruto, One piece, Bleach>'
        self.content_type = content_type
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class CohereModel(LLMModel):

    def __init__(self, content_type: str, model: str = "command-r7b-12-2024"):
        super().__init__(content_type)
        self.model = model
        api_key = os.getenv("COHERE_API_KEY")
        self.client = cohere.Client(api_key)

    def generate(self, prompt: str) -> str:
        message = f"Find comma separated {self.content_type} titles matching the prompt: {prompt}"
        response = self.client.chat(
            message=message,
            connectors=[{"id": "web-search"}],
            preamble=self.system_prompt,
            model=self.model,
            temperature=1.0
        )
        return response.text.strip()


class ModelHandler:
    
    @staticmethod
    def get_model(model_name: str, **kwargs) -> LLMModel:
        if model_name.lower() == "cohere":
            return CohereModel(**kwargs)
        else:
            raise ValueError(f"Model '{model_name}' is not supported.")

# ✅ Example usage
if __name__ == "__main__":
    
    model = ModelHandler.get_model("cohere", content_type='anime')
    
    # Generate text
    prompt = "female mc"
    result = model.generate(prompt)
    
    print(result)
