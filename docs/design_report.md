# Evaluation Report: Multi-Agent Competitive Intelligence System

## System Design Choices

1. **Architecture Overview**

   * Modular multi-agent pattern with four core agents:

     * **SearchAgent**: Retrieves top `N` URLs and metadata from SerpAPI.
     * **SummarizerAgent**: Uses **meta-llama/Llama-3.1-8B-Instruct** (via Hugging Face API) to produce concise, 1–2 sentence summaries.
     * **VerifierAgent**: Rule-based filtering (domain blacklist, date recency, non-empty summaries).
     * **CoordinatorAgent**: Orchestrates search→summarize→verify→validate→export pipeline and implements short-term in-memory caching to prevent duplicate processing.

2. **Technology Stack**

   * **Python** for core logic.
   * **SerpAPI** for search results.
   * **Hugging Face Inference API** (meta-llama/Llama-3.1-8B-Instruct) for summarization.
   * **Streamlit** for the interactive UI (bonus).
   * **BeautifulSoup** for optional page scraping fallback.
   * **pydantic** guardrails for output schema validation (bonus).
   * **tldextract** + **dateutil** for domain extraction and date normalization (ISO 8601).
   * **In-memory Python dictionary** for caching processed URLs.

3. **Bonus Features Implemented**

   * **UI**: Streamlit interface with dropdowns (including “Other”) and dynamic results display.
   * **Guardrails**: Pydantic schema (`UpdateSchema`) to validate each output record.
   * **Prompt Refinement**: Basic logic to sanitize and standardize user queries before search.


## Challenges Faced

1. **Inconsistent Date Formats**

   * Handled both relative (e.g., '7 days ago') and absolute dates ('May 7, 2025') by normalizing to `YYYY-MM-DD`.

2. **Noisy or Unreliable Sources**

   * Top results often from YouTube, Reddit, low-authority blogs; mitigated via rule-based VerifierAgent and domain blacklist.

3. **Summarization Constraints**

   * Without local GPU, relied entirely on API calls to meta-llama model; incurred latency and rate-limit considerations.

4. **Memory & Duplicate Handling**

   * Implemented an in-memory set to avoid re-processing the same URLs within a session; persistent caching was outside scope.

## Suggestions & Limitations

* **Persistent Caching**: Integrate **Redis** or **LangChain Memory** to persist URL history and agent state across sessions.
* **PDF & Document Retrieval**: Current pipeline only scrapes HTML articles; adding direct PDF ingestion and parsing would expand source coverage.
* **Parallel Execution**: Leverage Python `asyncio` or multi-threading to speed up summarization and verification steps.
* **Advanced Trust Scoring**: Implement a weighted scoring system using domain authority, HTTPS, and article length to rank updates.
