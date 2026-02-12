from tavily import TavilyClient
import ollama
import json
import re
from config import TAVILY_API_KEY, OLLAMA_MODEL

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def generate_queries(product):
    return [
        f"{product} pharmacology review",
        f"{product} clinical trial",
        f"{product} cordycepin mechanism study",
        f"{product} toxicity safety study",
    ]


def clean_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


def extract_structured(text, url):
    prompt = f"""
Extract academic research information.

Return JSON:
{{
  "source_type":"paper",
  "title":"",
  "entity":"",
  "year":"",
  "country":"",
  "summary":"",
  "doi_or_patent":"",
  "url":"{url}"
}}
"""

    response = ollama.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt + text[:4000]}]
    )

    return json.loads(clean_json(response["message"]["content"]))
