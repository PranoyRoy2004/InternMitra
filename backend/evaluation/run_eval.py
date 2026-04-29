# run_eval.py - Main evaluation runner
# Runs all test questions through the AI and computes metrics
# This is how we measure and improve AI quality over time

import uuid
from evaluation.eval_dataset import EVAL_DATASET
from evaluation.metrics import (
    compute_keyword_score,
    compute_semantic_score,
    compute_overall_score,
    aggregate_metrics
)
from services.groq_client import chat_with_groq, get_system_prompt
from services.rag_service import build_rag_context
from models.database import get_connection


def get_ai_response(question: str) -> str:
    """
    Gets AI response for an evaluation question using RAG + Groq.
    Same pipeline as the real chat — no shortcuts.

    Args:
        question: The evaluation question

    Returns:
        AI response as a string
    """
    # Build RAG context for the question
    rag_context = build_rag_context(question)

    messages = [
        {"role": "system", "content": get_system_prompt("career_assistant")}
    ]

    # Inject RAG context if available
    if rag_context:
        messages.append({
            "role": "system",
            "content": rag_context
        })

    messages.append({"role": "user", "content": question})

    return chat_with_groq(messages, temperature=0.3, max_tokens=512)


def log_eval_result(run_id: str, question: str, expected: str, got: str, score: float):
    """
    Saves evaluation result to the database for historical tracking.

    Args:
        run_id: Unique ID for this evaluation run
        question: The test question
        expected: Expected keywords as a string
        got: AI's actual response
        score: Overall score for this question
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eval_logs (run_id, question, expected, got, score)
        VALUES (?, ?, ?, ?, ?)
    """, (run_id, question, expected, got, score))

    conn.commit()
    conn.close()


async def run_full_evaluation() -> dict:
    """
    Runs the complete evaluation pipeline:
    1. For each question in the dataset
    2. Get AI response
    3. Score it against expected keywords and topics
    4. Log results to database
    5. Return aggregated metrics

    Returns:
        Dict with run_id, metrics, and per-question details
    """
    run_id = str(uuid.uuid4())[:8]   # Short unique ID for this run
    print(f"\n🔍 Starting evaluation run: {run_id}")
    print(f"📊 Total questions: {len(EVAL_DATASET)}\n")

    all_scores = []
    details = []

    for i, item in enumerate(EVAL_DATASET):
        print(f"  ▶ [{i+1}/{len(EVAL_DATASET)}] {item['question'][:60]}...")

        # Get AI response for this question
        ai_response = get_ai_response(item["question"])

        # Compute keyword-based metrics
        keyword_metrics = compute_keyword_score(
            response=ai_response,
            expected_keywords=item["expected_keywords"]
        )

        # Compute semantic similarity
        semantic_score = compute_semantic_score(
            response=ai_response,
            expected_topics=item["expected_topics"]
        )

        # Compute overall combined score
        overall = compute_overall_score(keyword_metrics, semantic_score)

        # Build per-question result
        question_result = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "ai_response_preview": ai_response[:200] + "...",
            "keywords_found": keyword_metrics["keywords_found"],
            "keywords_total": keyword_metrics["keywords_total"],
            "precision": keyword_metrics["precision"],
            "recall": keyword_metrics["recall"],
            "f1": keyword_metrics["f1"],
            "semantic_score": semantic_score,
            "overall_score": overall
        }

        all_scores.append(question_result)
        details.append(question_result)

        # Log to database
        log_eval_result(
            run_id=run_id,
            question=item["question"],
            expected=", ".join(item["expected_keywords"]),
            got=ai_response,
            score=overall
        )

        print(f"     ✅ Score: {overall:.2%} | Keywords: {keyword_metrics['keywords_found']}/{keyword_metrics['keywords_total']}")

    # Aggregate all scores into summary metrics
    summary = aggregate_metrics(all_scores)

    print(f"\n{'='*50}")
    print(f"📈 EVALUATION RESULTS - Run {run_id}")
    print(f"{'='*50}")
    print(f"  Accuracy  : {summary['accuracy']:.2%}")
    print(f"  Precision : {summary['precision']:.2%}")
    print(f"  Recall    : {summary['recall']:.2%}")
    print(f"  F1 Score  : {summary['f1_score']:.2%}")
    print(f"{'='*50}\n")

    return {
        "run_id": run_id,
        "total": len(EVAL_DATASET),
        "accuracy": summary["accuracy"],
        "precision": summary["precision"],
        "recall": summary["recall"],
        "f1_score": summary["f1_score"],
        "details": details
    }