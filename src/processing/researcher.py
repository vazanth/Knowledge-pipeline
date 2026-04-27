import asyncio, json, re
from utils.constants import EXPAND_QUERY_PROMPT


class Researcher:

    def __init__(self, llm_client, tavily_client, jina_client) -> None:
        self.llm_client = llm_client
        self.tavily_client = tavily_client
        self.jina_client = jina_client

    async def run_pipeline(self, summary, on_update=None):
        expanded_queries = await self.expand_query(summary)
        if on_update:
            await on_update(
                "\n\n" + f"📡 *Searching {len(expanded_queries)} angles via Tavily...*"
            )

        tavily_search_results = await self.fetch_all_urls(expanded_queries)
        if on_update:
            await on_update(f"📄 Scraping {len(tavily_search_results)} sources...")

        content = await self.scrape_urls(tavily_search_results)

        for res in tavily_search_results:
            url = res["url"]

            if content.get(url) is None and len(res.get("content", "")) > 100:
                content[url] = res.get("content", "")

        return content, [item["url"] for item in tavily_search_results]

    async def expand_query(self, summary):
        response = await self.llm_client.generate(
            EXPAND_QUERY_PROMPT.format(summary=summary)
        )
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            return []
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return []

    async def fetch_all_urls(self, expanded_queries):
        tavily_tasks = [
            asyncio.to_thread(self.tavily_client.retrieve, q) for q in expanded_queries
        ]
        search_results = await asyncio.gather(*tavily_tasks)
        if not search_results:
            return []

        seen_urls = set()
        unique_results = []

        for results in search_results:
            for r in results:
                if (url := r["url"]) not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)

        return unique_results

    async def scrape_urls(self, tavily_urls):
        return await self.jina_client.process_urls(tavily_urls)
