from db import init_db, insert_intelligence
from research_engine import generate_queries, extract_structured
from tavily import TavilyClient
from config import TAVILY_API_KEY
import requests
from bs4 import BeautifulSoup
from db import fetch_all
from report_generator import export_csv


tavily = TavilyClient(api_key=TAVILY_API_KEY)


def scrape(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print("Scrape failed:", e)
        return None


def run_research(product):
    queries = generate_queries(product)

    for query in queries:
        print(f"\nSearching: {query}")
        results = tavily.search(query=query, max_results=2)

        for r in results.get("results", []):
            url = r["url"]
            print(f"Scraping: {url}")

            page_text = scrape(url)
            if not page_text:
                continue

            try:
                structured = extract_structured(page_text, url)
                insert_intelligence(structured)
                print("Inserted into DB.")
            except Exception as e:
                print("Extraction failed:", e)


data = fetch_all()
for row in data:
    print(row)


def main():
    print("Initializing Database...")
    init_db()

    print("Running Research Engine...")
    run_research("Cordyceps militaris")

    print("\nResearch run complete.")
    export_csv()




if __name__ == "__main__":
    main()
