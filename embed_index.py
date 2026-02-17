import os
import json
import logging
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


class InMemoryIndex:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.chunks = []

    def build(self, texts: List[str]):
        self.chunks = texts
        embs = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        # normalize for cosine
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.embeddings = embs / norms

    def save(self, path: str):
        ensure_dir = os.path.dirname(path)
        if ensure_dir:
            os.makedirs(ensure_dir, exist_ok=True)
        np.save(path + ".npy", self.embeddings)
        with open(path + ".json", "w", encoding="utf-8") as f:
            json.dump(self.chunks, f)

    def load(self, path: str):
        self.embeddings = np.load(path + ".npy")
        with open(path + ".json", "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

    def query(self, q: str, top_k: int = 5):
        q_emb = self.model.encode([q], convert_to_numpy=True)
        q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)
        sims = (self.embeddings @ q_emb.T).squeeze()
        idx = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i]), self.chunks[int(i)]) for i in idx]


if __name__ == "__main__":
    # quick test helper
    txt = """
    This is a short example document. It contains multiple sentences. Use it to verify chunking and embeddings.
    """
    chunks = chunk_text(txt, chunk_size=20, overlap=5)
    idx = InMemoryIndex()
    idx.build(chunks)
    print(idx.query("example document"))
