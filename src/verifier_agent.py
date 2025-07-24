import tldextract
from datetime import datetime
from dateutil import parser
import re

class VerifierAgent:
    """
    VerifierAgent filters out unreliable or irrelevant entries.

    """

    def __init__(self, max_months_old: int = 6, blacklist_domains=None):
        self.max_months_old = max_months_old
        self.blacklist_domains = blacklist_domains or ["youtube.com", "reddit.com"]

    def parse_date(self, date_str: str) -> datetime | None:
        try:
            return parser.parse(date_str)
        except Exception:
            return None

    def get_domain(self, url: str) -> str:
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"
    
    def parse_text(self, text: str) -> bool:
        """
        Extracts the main content from the text, if available.
        """
        # Remove non-alphanumeric characters
        main_content = re.sub(r'[^\w\s]', '', text)

        if not main_content.strip():
            return False

        return True

    def verify(self, entry: dict) -> tuple[bool, str]:
        """
        Returns (is_valid: bool, reason: str)
        """
        # Check update presence
        update = entry.get('update', '').strip()
        update_verify = self.parse_text(update)
        if not update_verify:
            return False, "Empty update text"

        # Domain check
        domain = self.get_domain(entry.get('link', ''))
        if domain in self.blacklist_domains:
            return False, f"Blacklisted domain: {domain}"

        # Date check
        date_str = entry.get('date', None)
        dt = self.parse_date(date_str) if date_str else None
        if not dt:
            return True, "Unparsable date"

        # Check recency
        now = datetime.now()
        age_months = (now.year - dt.year) * 12 + now.month - dt.month
        if age_months > self.max_months_old:
            return False, f"Outdated ({age_months} months old)"

        return True, "Verified"

if __name__ == '__main__':
    agent = VerifierAgent(max_months_old=6)
    samples = [
        {"update": "New AI feature", "source": "https://www.notion.com/releases", "date": "May 13, 2025"},
        {"update": "Video review", "source": "https://www.youtube.com/watch?v=xyz", "date": "May 1, 2025"},
        {"update": "Old update", "source": "https://techblog.com/feature", "date": "Jan 1, 2024"},
        {"update": "", "source": "https://technews.com/ai", "date": "Jun 1, 2025"}
    ]
    for e in samples:
        valid, reason = agent.verify(e)
        print(e, '=>', valid, reason)
