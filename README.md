# LLM Eval Framework

A pytest-based framework for automatically evaluating LLM outputs — faithfulness, hallucination detection, latency SLAs, and answer relevance. Runs in CI via GitHub Actions on every PR.

## Why this exists

Most AI applications are tested manually — someone reads the output and thinks "that looks right." This doesn't scale. This framework automates LLM quality checks so regressions are caught before they reach production.

## Live CI

Every push to main triggers the full evaluation suite automatically. Results are uploaded as a downloadable HTML report on every run.

---

## What it tests

### Faithfulness
Is the answer grounded in the source document? Uses semantic similarity between the answer and context to detect answers that drift from the source material.

### Hallucination detection
Does the answer contain claims not supported by the context? Answers below a similarity threshold of 0.3 are flagged as potentially hallucinated.

### Ignorance admission
When the answer isn't in the context, does the system say "I don't know"? This is tested explicitly — a system that admits ignorance is safer than one that guesses confidently.

### Latency SLA
Does the API respond within acceptable time limits? Configurable threshold (default 10 seconds). Catches performance regressions automatically.

### Answer relevance
Is the answer semantically related to the question that was asked? Catches cases where the model answers a different question than the one posed.

### Sentiment classification accuracy
Does Claude correctly classify positive, negative, and neutral text? Tests both label accuracy and confidence scores.

---

## Results
9 tests · 100% pass rate · ~30 seconds

| Test | What it checks |
|---|---|
| `test_answer_is_faithful_to_context` | Faithfulness score ≥ 0.4 |
| `test_no_hallucination_on_grounded_question` | Hallucination score < 0.3 |
| `test_admits_ignorance_for_out_of_context_question` | Says "I don't know" correctly |
| `test_response_within_10_seconds` | Latency ≤ 10s SLA |
| `test_latency_sla_helper` | SLA helper function unit test |
| `test_answer_relevant_to_question` | Relevance score ≥ 0.4 |
| `test_positive_sentiment` | Correctly classifies positive text |
| `test_negative_sentiment` | Correctly classifies negative text |
| `test_neutral_sentiment` | Correctly classifies neutral text |

---

## Quick start

### Prerequisites
- Python 3.11+
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### Setup

```bash
git clone https://github.com/arya312/llm-eval-framework
cd llm-eval-framework
pip install anthropic python-dotenv sentence-transformers pytest pytest-json-report
```

Create `.env`:
ANTHROPIC_API_KEY="your_key_here"

### Run tests

```bash
pytest tests/ -v
```

### Generate HTML report

```bash
pytest tests/ -v --json-report --json-report-file=eval_report.json
python src/report_generator.py
```

Open `eval_report.html` in your browser.

---

## Add it to your own project

Copy `src/evaluators.py` into your project and use the evaluation functions directly:

```python
from evaluators import faithfulness_score, contains_hallucination, latency_within_sla

# After getting an LLM response
score = faithfulness_score(answer, context)
hallucinated = contains_hallucination(answer, context)
on_time = latency_within_sla(latency_seconds, sla_seconds=10.0)

print(f"Faithful: {score} | Hallucinated: {hallucinated} | On time: {on_time}")
```

---

## GitHub Actions CI

Add `ANTHROPIC_API_KEY` to your repo secrets (Settings → Secrets → Actions) and the workflow runs automatically on every push and PR.

Download the HTML eval report from the Actions tab after each run.

---

## How it works
pytest test suite
↓
Claude API (ask_with_context, classify_sentiment)
↓
Evaluators (sentence-transformers similarity scoring)
↓
Pass / Fail assertions
↓
JSON report → HTML report → GitHub Actions artifact

---

## Tech stack

- **Claude** (Anthropic) — LLM being evaluated
- **sentence-transformers** — semantic similarity scoring for faithfulness and relevance
- **pytest** — test framework and runner
- **pytest-json-report** — structured JSON output for report generation
- **GitHub Actions** — CI pipeline

---

Built by [arya312](https://github.com/arya312)
