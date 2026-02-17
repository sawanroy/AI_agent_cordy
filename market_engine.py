import logging
import json
import re
from tavily import TavilyClient
from config import TAVILY_API_KEY
import ollama
from config import OLLAMA_MODEL
from db import insert_intelligence
from pdf_pipeline import find_pdf_links, download_pdfs, extract_text_from_pdf


def generate_market_queries(product):
    """Generate diverse market research queries."""
    return [
        f"{product} market size 2024 2025 billion",
        f"{product} market cap valuation",
        f"{product} global market share",
        f"{product} market growth forecast",
        f"{product} companies manufacturers suppliers",
        f"{product} cordyceps industry leaders competitors",
        f"{product} nutraceutical supplement market analysis",
        f"{product} market trends revenue forecast",
    ]


def extract_market_intelligence(text, url):
    """Use Llama to extract market-specific intelligence."""
    prompt = """
Extract market intelligence from the following text. Return JSON with these fields:
{
  "source_type":"market_report",
  "market_size":"",
  "market_cap":"",
  "market_growth":"",
  "competitors":"",
  "key_players":"",
  "market_forecast":"",
  "summary":"",
  "url":"%s"
}
Only include fields you can confidently extract. If not mentioned, leave blank.
""" % url

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt + text[:5000]}]
        )
        content = response.get("message", {}).get("content", "")
        # Extract JSON
        match = re.search(r"\{.*?\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            data = {}
    except Exception:
        logging.exception("Market extraction failed for %s", url)
        data = {}

    # Ensure required keys
    defaults = {
        "source_type": "market_report",
        "market_size": "",
        "market_cap": "",
        "market_growth": "",
        "competitors": "",
        "key_players": "",
        "market_forecast": "",
        "summary": "",
        "url": url,
    }
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data


def run_market_research(product):
    """Run market intelligence research and store in DB."""
    if not TAVILY_API_KEY:
        logging.warning("TAVILY_API_KEY not set; skipping market research.")
        return

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    queries = generate_market_queries(product)

    for query in queries:
        logging.info("Market search: %s", query)
        try:
            results = tavily.search(query=query, max_results=3)
        except Exception:
            logging.exception("Tavily search failed for query: %s", query)
            continue

        for r in results.get("results", []):
            url = r.get("url", "")
            content = r.get("content", "")

            if not content:
                logging.warning("No content for %s", url)
                continue

            try:
                market_intel = extract_market_intelligence(content, url)
                if market_intel.get("market_size") or market_intel.get("competitors"):
                    # Insert into DB (we'll store as JSON string in summary)
                    insert_intelligence(market_intel)
                    logging.info("Inserted market intel: %s", market_intel.get("summary", "")[:100])
                
                # Auto-download PDFs from this page
                try:
                    pdf_links = find_pdf_links(content, url)
                    if pdf_links:
                        logging.info("Found %d PDF links on %s", len(pdf_links), url)
                        downloaded = download_pdfs(pdf_links, out_dir="pdfs/market")
                        if downloaded:
                            logging.info("Downloaded %d PDFs from market research", len(downloaded))
                        else:
                            logging.warning("Failed to download any of %d found PDFs from %s", len(pdf_links), url)
                    else:
                        logging.debug("No PDF links found in market research page: %s", url)
                except Exception:
                    logging.exception("Failed to download PDFs from %s", url)
            except Exception:
                logging.exception("Failed to process market data from %s", url)
