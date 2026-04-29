# rag_service.py - Retrieval Augmented Generation (RAG) system
# RAG = Find relevant knowledge first, then give it to the AI as context
# This makes the AI more accurate and reduces hallucination

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ── Load the embedding model ──────────────────────────────────────────────────
# This model converts text into vectors (lists of numbers)
# Similar texts will have similar vectors - that's how we find relevant content
print("⏳ Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded.")

# ── Load knowledge base from JSON ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_knowledge_base():
    """Load the career/internship knowledge base from JSON file."""
    path = os.path.join(DATA_DIR, "knowledge_base.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_internships():
    """Load the internship listings from JSON file."""
    path = os.path.join(DATA_DIR, "internships.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ── Pre-compute embeddings at startup ─────────────────────────────────────────
# We compute embeddings once when the server starts to keep things fast
knowledge_base = load_knowledge_base()
internships = load_internships()

# Create embeddings for each knowledge base entry
kb_texts = [item["content"] for item in knowledge_base]
kb_embeddings = embedding_model.encode(kb_texts, show_progress_bar=False)

# Create embeddings for internship descriptions
int_texts = [
    f"{item['role']} {' '.join(item['skills'])} {item['description']}"
    for item in internships
]
int_embeddings = embedding_model.encode(int_texts, show_progress_bar=False)

print("✅ RAG embeddings ready.")


def retrieve_relevant_knowledge(query: str, top_k: int = 3) -> list:
    """
    Find the most relevant knowledge base entries for a given query.
    
    Args:
        query: The user's question or topic
        top_k: How many results to return
    
    Returns:
        List of relevant knowledge entries with scores
    """
    # Convert the query to a vector
    query_embedding = embedding_model.encode([query], show_progress_bar=False)

    # Calculate similarity between query and all knowledge base entries
    similarities = cosine_similarity(query_embedding, kb_embeddings)[0]

    # Get top_k most similar entries
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.2:  # Only include if similarity is meaningful
            results.append({
                "topic": knowledge_base[idx]["topic"],
                "content": knowledge_base[idx]["content"],
                "score": float(similarities[idx])
            })

    return results


def retrieve_relevant_internships(skills: list, interests: str, top_k: int = 3) -> list:
    """
    Find the most relevant internships based on user skills and interests.
    
    Args:
        skills: List of user's skills
        interests: User's interest description
        top_k: How many internships to return
    
    Returns:
        List of relevant internship entries
    """
    # Combine skills and interests into a search query
    query = f"{' '.join(skills)} {interests}"
    query_embedding = embedding_model.encode([query], show_progress_bar=False)

    # Calculate similarity with all internships
    similarities = cosine_similarity(query_embedding, int_embeddings)[0]

    # Get top matches
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        entry = internships[idx].copy()
        entry["similarity_score"] = float(similarities[idx])
        results.append(entry)

    return results


def build_rag_context(query: str) -> str:
    """
    Build a context string from relevant knowledge to inject into the AI prompt.
    This is what makes the AI give more accurate, grounded answers.
    
    Args:
        query: The user's question
    
    Returns:
        A formatted context string to include in the prompt
    """
    relevant = retrieve_relevant_knowledge(query, top_k=3)

    if not relevant:
        return ""

    context_parts = ["Here is some relevant information to help answer the question:"]
    for item in relevant:
        context_parts.append(f"\n[{item['topic'].upper()}]\n{item['content']}")

    return "\n".join(context_parts)