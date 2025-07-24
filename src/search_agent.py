import os
import requests
import json
import re

from datetime import datetime, timedelta
from dateutil import parser


from dotenv import load_dotenv
load_dotenv()

class SearchAgent:
    """
    SearchAgent fetches top N relevant URLs for a given query using SerpAPI.

    Response Format:
    {
        "title": "Article title",
        "source": "URL of the source",
        "description": "Brief description of the update",
        "date": "Date of the update"
    }
    """

    def __init__(self, api_key: str | None = None , num_results: int = 5):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key or self.api_key == "None":
            raise ValueError("SERPAPI_API_KEY not provided or set in environment.")
        self.num_results = num_results
        self.base_url = "https://google.serper.dev/search"

    def parse_date(self, date_str: str) -> datetime | None:
        if not date_str:
            return None

        date_str = date_str.lower().strip()
        now = datetime.now()

        if 'ago' in date_str:
            match = re.match(r"(\\d+)\\s+(day|month|week|hour|minute)s?\\s+ago", date_str)
            if match:
                num, unit = int(match.group(1)), match.group(2)
                if unit == 'day':
                    return now - timedelta(days=num)
                elif unit == 'week':
                    return now - timedelta(weeks=num)
                elif unit == 'month':
                    return now - timedelta(days=num * 30) 
                elif unit == 'hour':
                    return now - timedelta(hours=num)
                elif unit == 'minute':
                    return now - timedelta(minutes=num)

        # Absolute dates: try parsing normally
        try:
            return parser.parse(date_str)
        except Exception:
            return None

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
            item_date = self.parse_date(item.get("date", ""))
            results.append({
                "title": item.get("title"),
                "source": item.get("link"),
                "description": item.get("snippet", "No description available"),
                "date": str(item_date.date()) if item_date else "Not Available"
            })
        return results

if __name__ == "__main__":
    agent = SearchAgent(num_results=5)
    query = "Notion AI new features 2025"
    results = agent.search(query)
    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['title']} - {item['source']}")
        print(f"   Description: {item['description']}")
        print(f"   Date: {item['date']}")