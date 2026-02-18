import logging
import json
import re
from tavily import TavilyClient
from config import TAVILY_API_KEY, OLLAMA_MODEL
import ollama
from db import insert_intelligence
from pdf_pipeline import find_pdf_links, download_pdfs


def generate_vendor_queries(product):
    """Generate diverse vendor/supplier search queries."""
    return [
        f"{product} supplier distributor vendor",
        f"{product} seller buy online",
        f"{product} manufacturer bulk wholesale",
        f"{product} GMP certified producer",
        f"{product} exporter company contact",
        f"{product} wholesale price quotation",
        f"{product} retailer distributor network",
        f"{product} herb supplier certification",
    ]


def clean_json(text):
    """Extract JSON from text using non-greedy regex."""
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


def extract_vendor_intelligence(text, url):
    """Use Llama to extract vendor-specific intelligence."""
    prompt = """
Extract vendor/supplier information from the following text. Return JSON with these fields:
{
  "source_type":"vendor",
  "vendor_name":"",
  "title":"",
  "entity":"",
  "country":"",
  "summary":"",
  "price":"",
  "moq":"",
  "certifications":"",
  "product_line":"",
  "contact_email":"",
  "phone":"",
  "website":"",
  "url":"%s"
}
Only include fields you can confidently extract. If not mentioned, leave blank.
""" % url

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt + text[:5000]}]
        )
        content = response.get("message", {}).get("content", "")
        try:
            data = json.loads(content)
        except Exception:
            data = json.loads(clean_json(content))
    except Exception:
        logging.exception("Vendor extraction failed for %s", url)
        data = {}

    # Ensure required keys
    defaults = {
        "source_type": "vendor",
        "vendor_name": "",
        "title": "",
        "entity": "",
        "country": "",
        "summary": "",
        "price": "",
        "moq": "",
        "certifications": "",
        "product_line": "",
        "contact_email": "",
        "phone": "",
        "website": "",
        "url": url,
    }
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data


def run_vendor_research(product):
    """Run vendor/supplier intelligence research and store in DB."""
    if not TAVILY_API_KEY:
        logging.warning("TAVILY_API_KEY not set; skipping vendor research.")
        return

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    queries = generate_vendor_queries(product)

    for query in queries:
        logging.info("Vendor search: %s", query)
        try:
            results = tavily.search(query=query, max_results=4)
        except Exception:
            logging.exception("Tavily search failed for query: %s", query)
            continue

        for r in results.get("results", []):
            url = r.get("url", "")
            content = r.get("content", "")

            if not content:
                logging.warning("No content for vendor URL: %s", url)
                continue

            try:
                vendor_intel = extract_vendor_intelligence(content, url)
                
                # Insert if we found vendor contact or pricing info
                if vendor_intel.get("vendor_name") or vendor_intel.get("contact_email") or vendor_intel.get("price"):
                    insert_intelligence(vendor_intel)
                    logging.info(
                        "Inserted vendor intel: %s from %s",
                        vendor_intel.get("vendor_name", "Unknown"),
                        vendor_intel.get("country", "Unknown"),
                    )
                
                # Auto-download PDFs from vendor page
                try:
                    pdf_links = find_pdf_links(content, url)
                    if pdf_links:
                        logging.info("Found %d PDF links on vendor page %s", len(pdf_links), url)
                        downloaded = download_pdfs(pdf_links, out_dir="pdfs/vendors")
                        if downloaded:
                            logging.info("Downloaded %d PDFs from vendor page", len(downloaded))
                        else:
                            logging.warning("Failed to download PDFs from vendor page %s", url)
                    else:
                        logging.debug("No PDF links found on vendor page: %s", url)
                except Exception:
                    logging.exception("Failed to download PDFs from vendor page %s", url)
            except Exception:
                logging.exception("Failed to process vendor data from %s", url)
