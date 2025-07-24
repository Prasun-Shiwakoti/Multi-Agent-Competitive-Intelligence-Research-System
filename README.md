# Multi-Agent Competitive Intelligence Research System

A Python-based multi-agent system that retrieves, summarizes, verifies, and presents competitive intelligence on AI productivity tools (e.g., Notion AI, ChatGPT, Grammarly). Includes a Streamlit UI, schema guardrails, in-memory caching, and prompt refinement.



## Features

* **SearchAgent**: Fetches top N search results via SerpAPI.
* **SummarizerAgent**: Uses `meta-llama/Llama-3.1-8B-Instruct` to generate concise summaries.
* **VerifierAgent**: Rule-based filtering by domain blacklist, date recency, and non-empty summaries.
* **CoordinatorAgent**: Orchestrates the pipeline, implements guardrails (Pydantic), and in-memory URL caching.
* **Streamlit UI** : Dropdown + custom input, result display.
* **Guardrails** : Pydantic schema validation (`UpdateSchema`).
* **Prompt Refinement**: Sanitize and standardize queries before search.


## Repository Structure

```
├── src/
│   ├── search_agent.py
│   ├── summarizer_agent.py
│   ├── verifier_agent.py
│   ├── coordinator.py
│   └── streamlit_app.py
├── outputs/       
├── logs/                
├── docs/
│   └── design_report.md
├── .gitignore
├── requirements.txt
└── README.md
```


## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Prasun-Shiwakoti/Multi-Agent-Competitive-Intelligence-Research-System
   cd Multi-Agent-Competitive-Intelligence-Research-System/src
   ```

2. **Create & activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate   
   venv\Scripts\activate    
   ```

3. **Install dependencies**:

   ```bash
   pip install -r ../requirements.txt
   ```

4. **Set environment variables**:

   ```bash
   export SERPAPI_API_KEY="your_serpapi_key"
   export HF_API_KEY="your_hf_api_key"
   ```



##  Usage

### 1. Command-Line Pipeline

```bash
python src/coordinator.py
```

* Adjust `product_name`, `num_results` and `query` inside the `__main__` block as needed.
* Outputs saved to `outputs/<product_name>.json`.

### 2. Streamlit UI

```bash
streamlit run src/streamlit_app.py
```

* Choose from predefined products or enter a custom topic.
* Slide to select number of results.
* Enter the desired prompt.
* Click **Run Intelligence Pipeline** and view structured results in the browser.



## Architecture & Agent Design

1. **SearchAgent** (`search_agent.py`)

   * Queries SerpAPI (Google engine)
   * Returns list of `{title, link, snippet, date}`.

2. **SummarizerAgent** (`summarizer_agent.py`)

   * Takes each search result, parses the snippet and scrapes full page.
   * Calls `meta-llama/Llama-3.1-8B-Instruct` via Hugging Face API for summary.
   * Outputs structured `{product, update, source, date}`.

3. **VerifierAgent** (`verifier_agent.py`)

   * Rule-based checks:

     * Domain blacklist (`youtube.com`, `reddit.com`, etc.)
     * Date recency (≤6 months; normalized to ISO `YYYY-MM-DD`).
     * Non-empty summary.

4. **CoordinatorAgent** (`coordinator.py`)

   * Orchestrates search → summarize → verify → guardrail validation (Pydantic) → export.
   * Implements in-memory caching to avoid duplicate URL processing.
   * Logs all operations to `logs/pipeline.log`.

5. **Streamlit UI** (`streamlit_app.py`)

   * Provides interactive controls and displays results dynamically.


## 📝 TODOs & Known Limitations

* **Persistent Caching**: Integrate Redis or LangChain Memory for cross-session URL caching.
* **PDF & Document Ingestion**: Currently only supports HTML articles; add PDF parsing.
* **Parallel Execution**: Use `asyncio` or threads to speed up summarization and verification.
* **Enhanced Trust Scoring**: Implement domain authority metrics for ranking updates.
