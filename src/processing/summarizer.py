import asyncio
from processing.chunk import get_chunks, token_len

from utils.constants import (
    CREATE_DIRECT_PROMPT,
    CREATE_LIST_REDUCE_PROMPT,
    CREATE_MAP_PROMPT,
    CREATE_REDUCE_PROMPT,
)

MAX_CONCURRENCY = 5  # max parallel LLM calls
MIN_VALID_SUMMARIES = 2  # fail fast if too few articles succeeded
MAX_RETRIES = 2


class Summarizer:
    def __init__(self, default_llm_client, gemini_llm_client) -> None:
        self.default_llm_client = default_llm_client
        self.gemini_llm_client = gemini_llm_client
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def run_pipeline(self, transcript) -> tuple[str, str]:
        limit = 5000

        total_token = token_len(transcript)
        if total_token < limit:
            prompt = CREATE_DIRECT_PROMPT.format(text=transcript)
            final_summary = await self._generate(prompt)
            return (final_summary, "stuff")
        else:
            # chunking
            chunks = get_chunks(transcript)
            # map step
            partial_summaries = []
            for chunk in chunks:
                map_prompt = CREATE_MAP_PROMPT.format(text=chunk)
                summary = await self._generate(map_prompt)
                partial_summaries.append(summary)

            # reduce step
            reduce_prompt = CREATE_REDUCE_PROMPT.format(
                combined="\n".join(partial_summaries)
            )
            final_summary = await self._generate(reduce_prompt)
            return (final_summary, "Map-Reduce")

    async def run_pipeline_list(self, transcripts: list[str]) -> str:
        tasks = [self._safe_summarize(i, text) for i, text in enumerate(transcripts)]
        results = await asyncio.gather(*tasks)

        valid = [r for r in results if r is not None]

        if len(valid) < MIN_VALID_SUMMARIES:
            raise RuntimeError(
                f"Too few valid summaries ({len(valid)}). "
                "Check Jina scrape quality or LLM errors."
            )

        combined = "\n\n---\n\n".join(valid)
        return await self._generate(
            CREATE_LIST_REDUCE_PROMPT.format(combined=combined), use_gemini=True
        )

    async def _safe_summarize(self, index, text):
        async with self.semaphore:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    summary, strategy = await self.run_pipeline(text)
                    return summary
                except Exception as e:
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(2**attempt)
            return None

    async def _generate(self, prompt: str, use_gemini=False) -> str:
        if use_gemini:
            response = await self.gemini_llm_client.generate(prompt)
            return response
        response = await self.default_llm_client.generate(prompt)
        return response
