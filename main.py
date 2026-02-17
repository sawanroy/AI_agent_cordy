import logging
import requests
from bs4 import BeautifulSoup
from config import TAVILY_API_KEY
from research_engine import generate_queries, extract_structured, auto_download_pdfs
from market_engine import run_market_research
from tavily import TavilyClient
from db import init_db, insert_intelligence, fetch_all
from report_generator import export_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if TAVILY_API_KEY:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
else:
    tavily = None
    logging.warning("TAVILY_API_KEY not set; Tavily searches disabled.")


def scrape(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Auto-download PDFs found on this page
        auto_download_pdfs(html, url)
        
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        # Limit size sent to downstream processors
        return text[:20000]
    except Exception as e:
        logging.exception("Scrape failed for %s", url)
        return None


def run_research(product):
    queries = generate_queries(product)

    for query in queries:
        logging.info("Searching: %s", query)
        if not tavily:
            logging.error("Tavily client unavailable; skipping search.")
            return
        results = tavily.search(query=query, max_results=2)

        for r in results.get("results", []):
            url = r["url"]
            logging.info("Scraping: %s", url)

            page_text = scrape(url)
            if not page_text:
                continue

            try:
                structured = extract_structured(page_text, url)
                # Basic validation
                if not structured.get("title") and not structured.get("url"):
                    logging.warning("Extracted structure missing title/url; skipping.")
                    continue
                insert_intelligence(structured)
                logging.info("Inserted into DB: %s", structured.get("title"))
            except Exception as e:
                logging.exception("Extraction failed for %s", url)


def main():
    logging.info("Initializing Database...")
    init_db()

    logging.info("Running Research Engine...")
    run_research("Cordyceps militaris")

    logging.info("Running Market Research Engine...")
    run_market_research("Cordyceps militaris")

    logging.info("Research run complete. Exporting CSV...")
    export_csv()
    # Optional: display rows
    rows = fetch_all()
    for row in rows:
        logging.debug(row)




if __name__ == "__main__":
    main()
