# metrics.py - Computes AI evaluation metrics

import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

# Lazy load the embedding model
_eval_model = None

def get_eval_model():
    global _eval_model
    if _eval_model is None:
        from sentence_transformers import SentenceTransformer
        _eval_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _eval_model


def compute_keyword_score(response: str, expected_keywords: list) -> dict:
    response_lower = response.lower()
    y_true = [1] * len(expected_keywords)
    y_pred = [1 if kw.lower() in response_lower else 0 for kw in expected_keywords]
    hits = sum(y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    return {
        "keywords_found": hits,
        "keywords_total": len(expected_keywords),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "keyword_hits": [
            {"keyword": kw, "found": bool(y_pred[i])}
            for i, kw in enumerate(expected_keywords)
        ]
    }


def compute_semantic_score(response: str, expected_topics: list) -> float:
    from sklearn.metrics.pairwise import cosine_similarity
    if not expected_topics:
        return 0.0
    model = get_eval_model()
    response_embedding = model.encode([response])
    topic_embeddings = model.encode(expected_topics)
    similarities = cosine_similarity(response_embedding, topic_embeddings)[0]
    return round(float(np.mean(similarities)), 4)


def compute_overall_score(keyword_metrics: dict, semantic_score: float) -> float:
    keyword_f1 = keyword_metrics.get("f1", 0.0)
    overall = (0.6 * keyword_f1) + (0.4 * semantic_score)
    return round(overall, 4)


def aggregate_metrics(all_scores: list) -> dict:
    if not all_scores:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0}
    precisions = [s["precision"] for s in all_scores]
    recalls = [s["recall"] for s in all_scores]
    f1s = [s["f1"] for s in all_scores]
    overall_scores = [s["overall_score"] for s in all_scores]
    accuracy = sum(1 for s in overall_scores if s > 0.5) / len(overall_scores)
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(float(np.mean(precisions)), 4),
        "recall": round(float(np.mean(recalls)), 4),
        "f1_score": round(float(np.mean(f1s)), 4)
    }