from dotenv import load_dotenv
load_dotenv()

import json
import os
from datetime import datetime

def generate_report(json_path: str = "eval_report.json", output_path: str = "eval_report.html"):
    """Generate an HTML report from pytest JSON output"""

    # Load pytest results
    if not os.path.exists(json_path):
        print(f"No report found at {json_path} — run pytest first")
        return

    with open(json_path) as f:
        data = json.load(f)

    summary = data.get("summary", {})
    tests = data.get("tests", [])

    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    duration = round(data.get("duration", 0), 2)
    pass_rate = round((passed / total * 100) if total > 0 else 0, 1)

    # Build test rows
    rows = ""
    for test in tests:
        name = test["nodeid"].split("::")[-1]
        outcome = test["outcome"]
        dur = round(test.get("duration", 0), 3)
        color = "#22c55e" if outcome == "passed" else "#ef4444"
        icon = "✅" if outcome == "passed" else "❌"

        # Get stdout output if any
        stdout = ""
        if test.get("call", {}).get("stdout"):
            stdout = test["call"]["stdout"].strip()[:200]

        rows += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;font-family:monospace;font-size:13px">{name}</td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:center">
                <span style="background:{color};color:white;padding:3px 10px;border-radius:20px;font-size:12px">{icon} {outcome}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:center;font-size:13px;color:#64748b">{dur}s</td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;font-size:12px;color:#64748b;font-family:monospace">{stdout}</td>
        </tr>"""

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LLM Eval Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 2rem; background: #f8fafc; }}
        h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; }}
        .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 1.5rem 0; }}
        .card {{ background: white; border-radius: 12px; padding: 1.25rem; border: 1px solid #e2e8f0; }}
        .card-label {{ font-size: 12px; color: #64748b; margin-bottom: 4px; }}
        .card-value {{ font-size: 28px; font-weight: 700; }}
        table {{ width: 100%; background: white; border-radius: 12px; border-collapse: collapse; }}
        th {{ padding: 12px; background: #f1f5f9; text-align: left; font-size: 13px; color: #475569; }}
    </style>
</head>
<body>
    <h1>LLM Evaluation Report</h1>
    <p style="color:#64748b">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Duration: {duration}s</p>

    <div class="cards">
        <div class="card">
            <div class="card-label">Total tests</div>
            <div class="card-value">{total}</div>
        </div>
        <div class="card">
            <div class="card-label">Passed</div>
            <div class="card-value" style="color:#22c55e">{passed}</div>
        </div>
        <div class="card">
            <div class="card-label">Failed</div>
            <div class="card-value" style="color:{'#ef4444' if failed > 0 else '#22c55e'}">{failed}</div>
        </div>
        <div class="card">
            <div class="card-label">Pass rate</div>
            <div class="card-value" style="color:{'#22c55e' if pass_rate >= 80 else '#ef4444'}">{pass_rate}%</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test</th>
                <th style="text-align:center">Result</th>
                <th style="text-align:center">Duration</th>
                <th>Output</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>

    <p style="font-size:12px;color:#cbd5e1;text-align:center;margin-top:2rem">
        LLM Eval Framework · github.com/arya312/llm-eval-framework
    </p>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"\n{'='*50}")
    print(f"EVAL REPORT SUMMARY")
    print(f"{'='*50}")
    print(f"Total:     {total}")
    print(f"Passed:    {passed}")
    print(f"Failed:    {failed}")
    print(f"Pass rate: {pass_rate}%")
    print(f"Duration:  {duration}s")
    print(f"{'='*50}")
    print(f"HTML report saved to: {output_path}")


if __name__ == "__main__":
    generate_report()