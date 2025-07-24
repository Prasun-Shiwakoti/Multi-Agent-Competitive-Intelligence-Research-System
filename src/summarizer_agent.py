import os
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()


class SummarizerAgent:
    """
    SummarizerAgent extracts and summarizes content for a given search result entry
    using Hugging Face's Inference API.

    """

    def __init__(self, hf_model="meta-llama/Llama-3.1-8B-Instruct:novita"):
        self.api_url = f"https://router.huggingface.co/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}
        self.hf_model = hf_model

    def fetch_full_text(self, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n'.join(p.get_text() for p in paragraphs)
            return text[:2000]
        except Exception:
            return "An error occurred while fetching the full text."

    def hf_title_summarize(self, title: str) -> str:

        title_summarizing_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                                You need to find out the main subject of a prompt. You dont need to answer the prompt. Just find out the main subject and fill the 'subject' field only.
                                Example: 
                                    Prompt: Notion AI new features 2025
                                    Response: Notion AI
                                
                                User: 
                                Prompt: {title}
                                Response: <subject>
                            """,
                }
            ],
            "model": self.hf_model
        }

        response = requests.post(self.api_url, headers=self.headers, json=title_summarizing_payload, timeout=30)
    
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message'].get('content', '').strip()

    def hf_article_summarize(self, text: str) -> str:

        article_summarizing_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": """You are a article summarization assistant. Summarize the following article concisely in a few words. If no text is provided respond with empty string ' '. 
                    Example: New meeting summary feature added.

                    """
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            "model": self.hf_model
        }

        response = requests.post(self.api_url, headers=self.headers, json=article_summarizing_payload, timeout=30)
    
        response.raise_for_status()
        result = response.json()

        return result['choices'][0]['message'].get('content', '').strip()

    def summarize(self, entry: dict) -> dict:
        context = entry.get('description', 'No description available')
        title = entry.get('title', 'No title available')
        source = entry.get('source', 'No source available')
        full_text = self.fetch_full_text(source)
        
        if full_text:
            context = full_text

        product = self.hf_title_summarize(title)
        summary = self.hf_article_summarize(context)

        return {
            "product": product,
            "update": summary,
            "source": source,
            "date": entry.get('date')
        }

if __name__ == '__main__':
    sample = {
        "title": "What's New with Notion",
        "link": "https://www.notion.com/releases",
        "snippet": "Notion 2.51: AI Meeting Notes, Enterprise Search & more · May 13, 2025",
        "date": "May 13, 2025"
    }
    agent = SummarizerAgent()
    result = agent.summarize(sample)
    print(result)