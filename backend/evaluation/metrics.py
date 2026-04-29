# metrics.py - Computes AI evaluation metrics
# Measures how well the AI answers questions compared to expected answers
# Uses keyword matching + semantic similarity for real evaluation

import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Reuse the same embedding model for semantic scoring
print("⏳ Loading evaluator embedding model...")
eval_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Evaluator model ready.")


def compute_keyword_score(response: str, expected_keywords: list) -> dict:
    """
    Check how many expected keywords appear in the AI response.
    This is a simple but effective way to measure factual coverage.

    Args:
        response: The AI's actual response text
        expected_keywords: List of keywords we expect the AI to mention

    Returns:
        Dict with keyword hits, precision, recall, f1
    """
    response_lower = response.lower()

    # For each keyword, check if it appears in the response
    # These are binary labels: 1 = keyword found, 0 = not found
    y_true = [1] * len(expected_keywords)   # We expect all keywords
    y_pred = [
        1 if keyword.lower() in response_lower else 0
        for keyword in expected_keywords
    ]

    hits = sum(y_pred)
    total = len(expected_keywords)

    # Calculate metrics - zero_division=0 prevents errors on empty results
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return {
        "keywords_found": hits,
        "keywords_total": total,
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "keyword_hits": [
            {"keyword": kw, "found": bool(y_pred[i])}
            for i, kw in enumerate(expected_keywords)
        ]
    }


def compute_semantic_score(response: str, expected_topics: list) -> float:
    """
    Measures semantic similarity between the AI response and expected topics.
    This catches cases where the AI says the right thing in different words.

    Args:
        response: The AI's actual response
        expected_topics: List of topic strings we expect the response to cover

    Returns:
        Semantic similarity score between 0.0 and 1.0
    """
    if not expected_topics:
        return 0.0

    # Encode the response
    response_embedding = eval_embedding_model.encode([response])

    # Encode all expected topics
    topic_embeddings = eval_embedding_model.encode(expected_topics)

    # Get similarity between response and each topic
    similarities = cosine_similarity(response_embedding, topic_embeddings)[0]

    # Return the average similarity across all topics
    return round(float(np.mean(similarities)), 4)


def compute_overall_score(keyword_metrics: dict, semantic_score: float) -> float:
    """
    Combines keyword and semantic scores into one final score.
    Weighted: 60% keyword coverage + 40% semantic similarity.

    Args:
        keyword_metrics: Output from compute_keyword_score()
        semantic_score: Output from compute_semantic_score()

    Returns:
        Overall score between 0.0 and 1.0
    """
    keyword_f1 = keyword_metrics.get("f1", 0.0)

    # Weighted combination
    overall = (0.6 * keyword_f1) + (0.4 * semantic_score)
    return round(overall, 4)


def aggregate_metrics(all_scores: list) -> dict:
    """
    Aggregates scores from all evaluation questions into summary metrics.

    Args:
        all_scores: List of per-question score dicts

    Returns:
        Summary dict with accuracy, precision, recall, f1
    """
    if not all_scores:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0
        }

    precisions = [s["precision"] for s in all_scores]
    recalls = [s["recall"] for s in all_scores]
    f1s = [s["f1"] for s in all_scores]
    overall_scores = [s["overall_score"] for s in all_scores]

    # Accuracy = percentage of questions where overall score > 0.5
    accuracy = sum(1 for s in overall_scores if s > 0.5) / len(overall_scores)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(float(np.mean(precisions)), 4),
        "recall": round(float(np.mean(recalls)), 4),
        "f1_score": round(float(np.mean(f1s)), 4)
    }