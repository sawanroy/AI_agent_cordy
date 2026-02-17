import json
import re
import logging
import ollama
from config import OLLAMA_MODEL
from pdf_pipeline import find_pdf_links, download_pdfs


def generate_queries(product):
    return [
        f"{product} pharmacology review",
        f"{product} clinical trial",
        f"{product} cordycepin mechanism study",
        f"{product} toxicity safety study",
    ]


def clean_json(text):
    # non-greedy match to avoid capturing multiple JSON objects
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


def auto_download_pdfs(html, base_url):
    """Find and download PDFs from HTML page."""
    try:
        pdf_links = find_pdf_links(html, base_url)
        if pdf_links:
            logging.info("Found %d PDF links on %s", len(pdf_links), base_url)
            downloaded = download_pdfs(pdf_links, out_dir="pdfs/research")
            if downloaded:
                logging.info("Downloaded %d PDFs from research page", len(downloaded))
            else:
                logging.warning("Failed to download any of %d found PDFs", len(pdf_links))
            return downloaded
        else:
            logging.debug("No PDF links found on %s", base_url)
    except Exception:
        logging.exception("Failed to download PDFs from %s", base_url)
    return []


def extract_structured(text, url):
    prompt = """
Extract academic research information.

Return JSON:
{
    "source_type":"paper",
    "title":"",
    "entity":"",
    "year":"",
    "country":"",
    "summary":"",
    "doi_or_patent":"",
    "url":"%s"
}
""" % url

    response = ollama.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt + text[:4000]}]
    )

    content = response.get("message", {}).get("content", "")
    try:
        data = json.loads(content)
    except Exception:
        try:
            data = json.loads(clean_json(content))
        except Exception:
            logging.exception("Failed to parse JSON from model response")
            data = {}

    # Ensure required keys exist and add url
    keys = [
        "source_type",
        "title",
        "entity",
        "year",
        "country",
        "summary",
        "doi_or_patent",
        "url",
    ]
    for k in keys:
        data.setdefault(k, "")
    data["url"] = url
    return data
