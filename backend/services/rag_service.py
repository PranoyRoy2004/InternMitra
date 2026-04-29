# rag_service.py - RAG system with lazy model loading
# Model loads on first request instead of at startup (fixes Render timeout)

import json
import os
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ── Lazy loading - model loads only when first needed ─────────────────────────
_embedding_model = None
_kb_embeddings = None
_int_embeddings = None
_knowledge_base = None
_internships = None

def get_embedding_model():
    """Load embedding model only once, on first use."""
    global _embedding_model
    if _embedding_model is None:
        print("⏳ Loading embedding model (first request)...")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded.")
    return _embedding_model

def load_knowledge_base():
    """Load knowledge base from JSON file."""
    global _knowledge_base
    if _knowledge_base is None:
        path = os.path.join(DATA_DIR, "knowledge_base.json")
        with open(path, "r", encoding="utf-8") as f:
            _knowledge_base = json.load(f)
    return _knowledge_base

def load_internships():
    """Load internships from JSON file."""
    global _internships
    if _internships is None:
        path = os.path.join(DATA_DIR, "internships.json")
        with open(path, "r", encoding="utf-8") as f:
            _internships = json.load(f)
    return _internships

def get_kb_embeddings():
    """Compute knowledge base embeddings once and cache them."""
    global _kb_embeddings
    if _kb_embeddings is None:
        model = get_embedding_model()
        kb = load_knowledge_base()
        texts = [item["content"] for item in kb]
        _kb_embeddings = model.encode(texts, show_progress_bar=False)
    return _kb_embeddings

def get_int_embeddings():
    """Compute internship embeddings once and cache them."""
    global _int_embeddings
    if _int_embeddings is None:
        model = get_embedding_model()
        internships = load_internships()
        texts = [
            f"{item['role']} {' '.join(item['skills'])} {item['description']}"
            for item in internships
        ]
        _int_embeddings = model.encode(texts, show_progress_bar=False)
    return _int_embeddings


def retrieve_relevant_knowledge(query: str, top_k: int = 3) -> list:
    """Find most relevant knowledge base entries for a query."""
    from sklearn.metrics.pairwise import cosine_similarity

    model = get_embedding_model()
    kb = load_knowledge_base()
    kb_embeddings = get_kb_embeddings()

    query_embedding = model.encode([query], show_progress_bar=False)
    similarities = cosine_similarity(query_embedding, kb_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.2:
            results.append({
                "topic": kb[idx]["topic"],
                "content": kb[idx]["content"],
                "score": float(similarities[idx])
            })
    return results


def retrieve_relevant_internships(skills: list, interests: str, top_k: int = 3) -> list:
    """Find most relevant internships based on skills and interests."""
    from sklearn.metrics.pairwise import cosine_similarity

    model = get_embedding_model()
    internships = load_internships()
    int_embeddings = get_int_embeddings()

    query = f"{' '.join(skills)} {interests}"
    query_embedding = model.encode([query], show_progress_bar=False)
    similarities = cosine_similarity(query_embedding, int_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        entry = internships[idx].copy()
        entry["similarity_score"] = float(similarities[idx])
        results.append(entry)
    return results


def build_rag_context(query: str) -> str:
    """Build context string from relevant knowledge to inject into AI prompt."""
    relevant = retrieve_relevant_knowledge(query, top_k=3)
    if not relevant:
        return ""
    context_parts = ["Here is some relevant information to help answer the question:"]
    for item in relevant:
        context_parts.append(f"\n[{item['topic'].upper()}]\n{item['content']}")
    return "\n".join(context_parts)