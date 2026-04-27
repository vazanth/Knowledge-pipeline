from google import genai
from adapters.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self.client = genai.Client()

    async def generate(self, prompt: str) -> str:
        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text or ""
