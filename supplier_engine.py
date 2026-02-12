from tavily import TavilyClient
import ollama
import json
import re
from config import TAVILY_API_KEY, OLLAMA_MODEL

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def generate_queries(product):
    return [
        f"{product} GMP certified manufacturer",
        f"{product} bulk supplier India",
        f"{product} wholesale exporter China",
    ]


def clean_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


def extract_supplier(text, url):
    prompt = f"""
Extract supplier information.

Return JSON:
{{
  "source_type":"supplier",
  "title":"",
  "entity":"",
  "country":"",
  "price":"",
  "moq":"",
  "certifications":"",
  "contact_email":"",
  "phone":"",
  "url":"{url}"
}}
"""

    response = ollama.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt + text[:4000]}]
    )

    return json.loads(clean_json(response["message"]["content"]))
