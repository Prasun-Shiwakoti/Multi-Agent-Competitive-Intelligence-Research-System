import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()

class SearchAgent:
    """
    SearchAgent fetches top N relevant URLs for a given query using SerpAPI.
    Requires SERPAPI_API_KEY environment variable.
    """

    def __init__(self, api_key: str | None = None , num_results: int = 5):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key or self.api_key == "None":
            raise ValueError("SERPAPI_API_KEY not provided or set in environment.")
        self.num_results = num_results
        self.base_url = "https://google.serper.dev/search"

    def search(self, query: str) -> list[dict]:
        """
        Perform a search on SerpAPI and return a list of result dicts with 'title' and 'link'.
        """
        payload = json.dumps({
            "q": query,
            "num": self.num_results
        })
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(self.base_url, headers=headers, data=payload)

        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("organic", [])[: self.num_results]:
            results.append({
                "product": item.get("title"),
                "source": item.get("link"),
                "update": item.get("snippet", "No description available"),
                "date": item.get("date", "No date available")
            })
        return results

if __name__ == "__main__":
    agent = SearchAgent(num_results=5)
    query = "Notion AI new features 2025"
    results = agent.search(query)
    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['product']} - {item['source']}")
        print(f"   Update: {item['update']}")
        print(f"   Date: {item['date']}")