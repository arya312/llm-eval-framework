import pytest
import sys
sys.path.insert(0, ".")

from src.llm_client import ask_with_context, classify_sentiment
from src.evaluators import (
    faithfulness_score,
    answer_relevance_score,
    contains_hallucination,
    latency_within_sla
)

# Test context — excerpt from a real document
CONTEXT = """
The Transformer architecture was introduced in the paper "Attention Is All You Need" 
by Vaswani et al. in 2017. It uses self-attention mechanisms to process sequences 
in parallel, unlike RNNs which process tokens sequentially. The base Transformer 
model was trained for 100,000 steps taking 12 hours on 8 P100 GPUs. It achieved 
a BLEU score of 28.4 on the English-to-German translation task, setting a new 
state of the art at the time.
"""

TEST_CASES = [
    {
        "question": "What BLEU score did the Transformer achieve?",
        "expected_keywords": ["28.4", "english", "german"],
        "should_answer": True
    },
    {
        "question": "How long did training take?",
        "expected_keywords": ["12 hours", "100,000"],
        "should_answer": True
    },
    {
        "question": "What is the capital of France?",
        "expected_keywords": [],
        "should_answer": False  # Not in context — should say "I don't know"
    }
]


class TestRAGFaithfulness:
    """Tests that answers are grounded in source context"""

    def test_answer_is_faithful_to_context(self):
        """Faithfulness score should be above threshold for grounded answers"""
        result = ask_with_context(TEST_CASES[0]["question"], CONTEXT)
        score = faithfulness_score(result["answer"], CONTEXT)
        print(f"\nFaithfulness score: {score}")
        assert score >= 0.4, f"Answer not faithful enough: {score} < 0.4"

    def test_no_hallucination_on_grounded_question(self):
        """Should not hallucinate when answer is in context"""
        result = ask_with_context(TEST_CASES[0]["question"], CONTEXT)
        hallucinated = contains_hallucination(result["answer"], CONTEXT)
        print(f"\nAnswer: {result['answer'][:100]}")
        assert not hallucinated, "Answer appears to be hallucinated"

    def test_admits_ignorance_for_out_of_context_question(self):
        """Should say 'I don't know' when answer is not in context"""
        result = ask_with_context(TEST_CASES[2]["question"], CONTEXT)
        answer_lower = result["answer"].lower()
        print(f"\nAnswer: {result['answer']}")
        assert "don't know" in answer_lower or "not in" in answer_lower or "context" in answer_lower, \
            f"Should admit ignorance but answered: {result['answer']}"


class TestLatencySLA:
    """Tests that responses meet latency requirements"""

    def test_response_within_10_seconds(self):
        """Standard queries should complete within 10 seconds"""
        result = ask_with_context(TEST_CASES[0]["question"], CONTEXT)
        print(f"\nLatency: {result['latency_seconds']}s")
        assert latency_within_sla(result["latency_seconds"], sla_seconds=10.0), \
            f"Response too slow: {result['latency_seconds']}s > 10s"

    def test_latency_sla_helper(self):
        """Test the SLA helper function itself"""
        assert latency_within_sla(2.5, sla_seconds=5.0) is True
        assert latency_within_sla(6.0, sla_seconds=5.0) is False


class TestAnswerRelevance:
    """Tests that answers are relevant to questions"""

    def test_answer_relevant_to_question(self):
        """Answer should be semantically related to the question asked"""
        result = ask_with_context(TEST_CASES[1]["question"], CONTEXT)
        score = answer_relevance_score(result["answer"], TEST_CASES[1]["question"])
        print(f"\nRelevance score: {score}")
        assert score >= 0.4, f"Answer not relevant enough: {score} < 0.4"


class TestSentimentClassification:
    """Tests Claude's sentiment classification"""

    def test_positive_sentiment(self):
        result = classify_sentiment("This product is absolutely amazing and exceeded all my expectations!")
        print(f"\nSentiment: {result['sentiment']} ({result['confidence']})")
        assert result["sentiment"] == "positive"
        assert result["confidence"] >= 0.7

    def test_negative_sentiment(self):
        result = classify_sentiment("This is terrible. Completely broken and unusable.")
        print(f"\nSentiment: {result['sentiment']} ({result['confidence']})")
        assert result["sentiment"] == "negative"
        assert result["confidence"] >= 0.7

    def test_neutral_sentiment(self):
        result = classify_sentiment("The meeting is scheduled for Tuesday at 3pm.")
        print(f"\nSentiment: {result['sentiment']} ({result['confidence']})")
        assert result["sentiment"] == "neutral"