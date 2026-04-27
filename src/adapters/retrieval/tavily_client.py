from tavily import TavilyClient


class TavilyRetrievalClient:
    def __init__(self, api_key: str) -> None:
        self.client = TavilyClient(api_key=api_key)

    def retrieve(self, query: str, max_results: int = 2):
        response = self.client.search(
            query=query, search_depth="advanced", max_results=max_results
        )
        search_results = response.get("results", [])
        filtered_results = [
            result for result in search_results if result.get("score", 0) > 0.4
        ]
        return filtered_results
