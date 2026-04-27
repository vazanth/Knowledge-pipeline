import ollama

from adapters.llm.base import BaseLLMClient


class OllamaClient(BaseLLMClient):
    def __init__(self, model: str) -> None:
        self.model = model
        self.client = ollama.AsyncClient()

    async def generate(self, prompt: str) -> str:
        response = await self.client.generate(model=self.model, prompt=prompt)
        return response["response"]
