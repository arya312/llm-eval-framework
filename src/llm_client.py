from dotenv import load_dotenv
load_dotenv()

import os
import time
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def ask_with_context(question: str, context: str, max_tokens: int = 512) -> dict:
    """
    Ask Claude a question grounded in a context document.
    Returns answer, latency, and token usage.
    """
    start = time.time()

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't know based on the document."

Context:
{context}

Question: {question}"""
        }]
    )

    latency = round(time.time() - start, 3)

    return {
        "answer": message.content[0].text,
        "latency_seconds": latency,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "model": message.model
    }


def classify_sentiment(text: str) -> dict:
    """
    Classify sentiment of text.
    Returns label and confidence score.
    """
    start = time.time()

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"""Classify the sentiment of this text.
Return ONLY a JSON object like: {{"sentiment": "positive", "confidence": 0.95}}
Valid sentiments: positive, negative, neutral

Text: {text}"""
        }]
    )

    latency = round(time.time() - start, 3)
    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    result["latency_seconds"] = latency
    return result