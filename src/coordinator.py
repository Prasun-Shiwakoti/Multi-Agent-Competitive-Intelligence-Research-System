import json
import logging
from pathlib import Path

from search_agent import SearchAgent
from summarizer_agent import SummarizerAgent
from verifier_agent import VerifierAgent
from pydantic import BaseModel, HttpUrl, ValidationError


LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / 'pipeline.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class UpdateSchema(BaseModel):
    product: str
    update: str
    source: HttpUrl
    date: str

    class Config:
        str_strip_whitespace = True

class CoordinatorAgent:
    """
    Orchestrates the pipeline:
      1. Search
      2. Summarize
      3. Verify
      4. Validate
      5. Export results
    """

    def __init__(
        self,
        product_name: str,
        num_results: int = 5,
        max_months_old: int = 6,
        output_dir: str = 'outputs'
    ):
        self.product_name = product_name
        self.num_results = num_results
        self.search_agent = SearchAgent(num_results=num_results * 2)
        self.summarizer = SummarizerAgent(hf_model="meta-llama/Llama-3.1-8B-Instruct:novita")
        self.verifier = VerifierAgent(max_months_old=max_months_old, blacklist_domains=["youtube.com", "reddit.com"])

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.memory = dict()

        logger.info(f"Coordinator initialized for '{product_name}' with top {num_results} results and max age {max_months_old} months.")


    def run(self, query: str):

        #1 Refine query
        if len(query.strip()) > 50:
            logger.info(f"Refining query: {query}")
            query = self.summarizer.hf_prompt_refine(query)


        # 2. Search
        logger.info(f"Starting pipeline run for query: '{query}'")
        raw_results = self.search_agent.search(query)

        # 3. Summarize & 4. Verify
        final_results = []
        for entry in raw_results:
            if entry['source'] in self.memory:
                logger.info(f"Skipping already processed entry: {entry['source']}")
                continue

            logger.info(f"Summarizing entry: {entry['title']}")
            summary = self.summarizer.summarize(entry)
            
            logger.info(f"Verifying summary for entry {entry['title']}")
            valid, reason = self.verifier.verify(summary)
            
            entry_record = {**summary, 'verified': valid, 'reason': reason}
            if not valid:
                logger.warning(f"Skipping: {summary['source']} ({reason})")
                continue
            
            self.memory[entry['source']] = entry_record

            try:
                validated = UpdateSchema(**summary)
                validated_dict = validated.model_dump()
                validated_dict['source'] = str(validated_dict['source'])
                validated_dict['product'] = self.product_name

                logger.info(f"Guardrail validation passed for entry {entry['title']}")
                final_results.append(validated_dict)
            except ValidationError as ve:
                logger.error(f"Guardrail validation failed for entry {entry['title']}: {ve}")
                continue

        # 5. Export
        logger.info(f"Exporting {len(final_results)} valid results to JSON.")
        self.export_json(final_results[:self.num_results])
        return final_results[:self.num_results]

    def export_json(self, items: list[dict]):
        path = self.output_dir / f"{self.product_name.lower().replace(' ', '_')}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4)
        logger.info(f"JSON output saved to {path}")


if __name__ == '__main__':
    agent = CoordinatorAgent(product_name="Notion AI", num_results=5)
    results = agent.run(query="Notion AI new features 2025")
    # print("Final Results:", results)
