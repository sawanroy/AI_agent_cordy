import os
import re
import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def find_pdf_links(html, base_url):
    """Find PDF links in HTML or plain text content."""
    links = []
    
    # Try parsing as HTML first
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf") or "application/pdf" in (a.get("type") or ""):
            links.append(urljoin(base_url, href))
    
    # Also search for PDF URLs in plain text (for Tavily snippets)
    pdf_urls = re.findall(r'https?://[^\s"<>]+\.pdf', html)
    for url in pdf_urls:
        full_url = urljoin(base_url, url)
        if full_url not in links:
            links.append(full_url)
    
    if links:
        logging.info("Found %d PDF links on %s", len(links), base_url)
    else:
        logging.debug("No PDF links found on %s", base_url)
    
    return links


def download_pdf(url, out_dir="pdfs"):
    ensure_dir(out_dir)
    try:
        logging.debug("Attempting to download PDF: %s", url)
        r = requests.get(url, stream=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        parsed = urlparse(url)
        name = os.path.basename(parsed.path) or "download.pdf"
        # sanitize
        name = re.sub(r"[^0-9A-Za-z._-]", "_", name)
        out_path = os.path.join(out_dir, name)
        
        # Check file size
        content_length = r.headers.get('content-length')
        if content_length and int(content_length) > 100*1024*1024:  # >100MB
            logging.warning("PDF too large (%s bytes), skipping: %s", content_length, url)
            return None
        
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info("Downloaded PDF: %s", out_path)
        return out_path
    except requests.exceptions.HTTPError as e:
        logging.warning("HTTP error downloading PDF %s: %s", url, e)
        return None
    except Exception:
        logging.exception("Failed to download PDF: %s", url)
        return None


def download_pdfs(urls, out_dir="pdfs"):
    """Download multiple PDFs, return list of successfully downloaded paths."""
    if not urls:
        logging.debug("No PDFs to download.")
        return []
    
    results = []
    for u in urls:
        p = download_pdf(u, out_dir=out_dir)
        if p:
            results.append(p)
    return results


def extract_text_from_pdf(path):
    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)
    except Exception:
        logging.exception("PDF text extraction failed for %s", path)
        return ""


if __name__ == "__main__":
    # small demo: download PDFs linked from a URL
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_pipeline.py <webpage_url>")
        raise SystemExit(1)

    url = sys.argv[1]
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    pdfs = find_pdf_links(r.text, url)
    print("Found PDFs:", pdfs)
    downloaded = download_pdfs(pdfs)
    print("Downloaded:", downloaded)
