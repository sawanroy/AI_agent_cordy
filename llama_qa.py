import logging
from typing import List

import ollama
from config import OLLAMA_MODEL
from embed_index import InMemoryIndex


class LlamaQA:
    def __init__(self, index: InMemoryIndex, model: str = None):
        self.index = index
        self.model = model or OLLAMA_MODEL

    def answer(self, question: str, top_k: int = 5) -> str:
        # retrieve
        results = self.index.query(question, top_k=top_k)
        context = "\n\n---\n\n".join([r[2] for r in results])

        prompt = f"""
Use the following extracted document context to answer the question. If the answer is not contained, say you don't know.

Context:
{context}

Question: {question}
"""

        try:
            resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return resp.get("message", {}).get("content", "")
        except Exception:
            logging.exception("Llama query failed")
            return ""


if __name__ == "__main__":
    # demo usage (requires built index)
    import sys

    if len(sys.argv) < 2:
        print("Usage: python llama_qa.py 'your question'")
        raise SystemExit(1)

    q = sys.argv[1]
    idx = InMemoryIndex()
    idx.load("data/emb_index")
    qa = LlamaQA(idx)
    print(qa.answer(q))
