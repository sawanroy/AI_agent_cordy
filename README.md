# AI Company Intel

Overview
- Small research pipeline: scrape pages, extract structured intelligence, store in Postgres, export CSV.
- **Auto-downloads PDFs** from research and market pages to `pdfs/research` and `pdfs/market` folders.
- PDF pipeline: find/download PDFs, extract text, build embeddings, and query a local Llama via Ollama.

Requirements
- Python 3.9+ (tests used 3.12)
- See `requirements.txt` for Python packages.

Setup
- Create and activate a virtualenv:

```bash
python3 -m venv vendor_agent_env
source vendor_agent_env/bin/activate
pip install -r requirements.txt
```

- Provide environment variables (or use a `.env` file):

- `DB_NAME` (default: `cordyceps_intel`)
- `DB_USER` (default: `postgres`)
- `DB_PASSWORD` (required if Postgres requires auth)
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5432`)
- `TAVILY_API_KEY` (optional)
- `OLLAMA_MODEL` (default: `llama3`)

Run the main pipeline

```bash
# ensure DB is reachable and creds are set (export DB_PASSWORD=...)
# PDFs will be automatically downloaded from scraped pages to pdfs/research and pdfs/market
python3 main.py
```

PDF pipeline
- Download PDFs linked from a webpage:

```bash
python3 pdf_pipeline.py https://example.com/page-with-pdfs
```

- Extract text and build an embedding index (example):

```bash
python3 - <<'PY'
from pdf_pipeline import extract_text_from_pdf
from embed_index import chunk_text, InMemoryIndex
import glob, os

texts = []
for p in glob.glob('pdfs/*.pdf'):
    t = extract_text_from_pdf(p)
    if t:
        texts += chunk_text(t, chunk_size=500, overlap=100)

idx = InMemoryIndex()
idx.build(texts)
os.makedirs('data', exist_ok=True)
idx.save('data/emb_index')
PY
```

Querying with Llama (Ollama)
- Ensure `ollama` daemon is available and the model `OLLAMA_MODEL` is installed locally.
- Ask a question using the built index:

```bash
python3 llama_qa.py "What is cordycepin's mechanism of action?"
```

Notes and caveats
- Respect `robots.txt` and site terms of service before scraping/downloading.
- Do not download paywalled or copyrighted PDFs without permission.
- Large PDFs should be chunked before sending to LLMs; this repository uses a simple chunker and an in-memory index.
- For production use, replace the in-memory index with a persistent vector DB.

Market Intelligence (NEW)
- Enhanced market research with Tavily search for market cap, market size, and competitors.
- Queries generated: market size forecasts, company competitors, industry leaders, growth trends.
- Results extracted by Llama and stored in Postgres alongside academic research.
- **Auto-downloads PDFs** found on market research pages to `pdfs/market/`.
- Run automatically with main pipeline or alone via `market_engine.run_market_research()`.

Files of interest
- `main.py` — orchestrates scraping, market research, and DB storage.
- `market_engine.py` — Generate market queries and extract market intelligence (cap, size, competitors).
- `pdf_pipeline.py` — find/download/extract PDF text.
- `embed_index.py` — chunking and in-memory embedding index.
- `llama_qa.py` — retrieval + Ollama Llama QA wrapper.

License
- No license specified. Use code responsibly.
