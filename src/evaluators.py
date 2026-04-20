from sentence_transformers import SentenceTransformer, util
import re

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def faithfulness_score(answer: str, context: str) -> float:
    """
    Measures how grounded the answer is in the context.
    Score 0.0-1.0. Higher = more faithful to context.
    """
    model = get_model()
    answer_emb = model.encode(answer, convert_to_tensor=True)
    context_emb = model.encode(context, convert_to_tensor=True)
    score = float(util.cos_sim(answer_emb, context_emb)[0][0])
    return round(score, 3)


def answer_relevance_score(answer: str, question: str) -> float:
    """
    Measures how relevant the answer is to the question.
    Score 0.0-1.0. Higher = more relevant.
    """
    model = get_model()
    answer_emb = model.encode(answer, convert_to_tensor=True)
    question_emb = model.encode(question, convert_to_tensor=True)
    score = float(util.cos_sim(answer_emb, question_emb)[0][0])
    return round(score, 3)


def contains_hallucination(answer: str, context: str) -> bool:
    """
    Simple hallucination check.
    Returns True if answer contains specific claims not in context.
    """
    # If answer says "I don't know" it's not hallucinating
    if "i don't know" in answer.lower() or "not in the context" in answer.lower():
        return False

    # Check faithfulness — below 0.3 suggests hallucination
    score = faithfulness_score(answer, context)
    return score < 0.3


def latency_within_sla(latency_seconds: float, sla_seconds: float = 10.0) -> bool:
    """Check if response met latency SLA"""
    return latency_seconds <= sla_seconds