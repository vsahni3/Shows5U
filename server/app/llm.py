from abc import ABC, abstractmethod
import cohere

# idea for implementing comments + rating
# good rating means find similar descriptions
# comment is isolated from anime, use it as an additional way to match anime descritpions


class LLMModel(ABC):
    system_prompt = 'You are an anime recommender system that gives comma separated anime titles to the user'

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class CohereModel(LLMModel):
    system_message = {
    "role": "system",
    "content": LLMModel.system_prompt
}

    def __init__(self, api_key: str, model: str = "command"):
        self.api_key = api_key
        self.model = model
        self.client = cohere.Client(api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat(
            messages=[],
            connectors=[{"id": "web-search"}]
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
    API_KEY = "your_cohere_api_key_here"  # Replace with your Cohere API key
    
    # Instantiate Cohere model dynamically
    model = ModelHandler.get_model("cohere", api_key=API_KEY)
    
    # Generate text
    prompt = "Write a short story about AI and humanity."
    result = model.generate(prompt)
    
    print("Generated Text:", result)
