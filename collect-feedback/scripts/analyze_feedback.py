#!/usr/bin/env python3
"""
Analyze feedback log and extract patterns.

Usage:
    python analyze_feedback.py <path-to-feedback-log.md> [--output <path>]

Parses a structured feedback log (from the collect-feedback skill),
counts recurring themes across testers, and outputs a JSON analysis
with pattern frequencies and priority rankings.

The agent uses this output to decide which patterns become specs.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def parse_feedback_log(content: str) -> list[dict]:
    """Parse the markdown feedback log into structured tester data."""
    testers = []
    # Split by tester sections (## Tester N)
    sections = re.split(r'^## Tester \d+', content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip header before first tester
        tester = {
            "name": "",
            "source": "",
            "test_completed": "",
            "stuck_points": "",
            "responses": {
                "stuck_confused": "",
                "expected_not_happened": "",
                "first_change": "",
                "would_use": "",
                "would_pay": "",
            },
            "quotes": [],
            "interpretation": "",
        }

        # Extract metadata
        name_match = re.search(r'\*\*Name/Handle:\*\*\s*(.*)', section)
        if name_match:
            tester["name"] = name_match.group(1).strip()

        source_match = re.search(r'\*\*Source:\*\*\s*(.*)', section)
        if source_match:
            tester["source"] = source_match.group(1).strip()

        completed_match = re.search(r'\*\*Test completed:\*\*\s*(.*)', section)
        if completed_match:
            tester["test_completed"] = completed_match.group(1).strip().lower()

        stuck_match = re.search(r'\*\*Stuck points:\*\*\s*(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL)
        if stuck_match:
            tester["stuck_points"] = stuck_match.group(1).strip()

        # Extract responses
        response_patterns = [
            (r'1\.\s*\*\*Stuck/confused:\*\*\s*(.*?)(?=\n\d\.|\n###|\Z)', "stuck_confused"),
            (r'2\.\s*\*\*Expected but didn\'t happen:\*\*\s*(.*?)(?=\n\d\.|\n###|\Z)', "expected_not_happened"),
            (r'3\.\s*\*\*First thing to change:\*\*\s*(.*?)(?=\n\d\.|\n###|\Z)', "first_change"),
            (r'4\.\s*\*\*Would use tomorrow.*?:\*\*\s*(.*?)(?=\n\d\.|\n###|\Z)', "would_use"),
            (r'5\.\s*\*\*Would pay for:\*\*\s*(.*?)(?=\n###|\n---|\Z)', "would_pay"),
        ]
        for pattern, key in response_patterns:
            match = re.search(pattern, section, re.DOTALL)
            if match:
                tester["responses"][key] = match.group(1).strip()

        # Extract quotes
        quotes = re.findall(r'>\s*(.*)', section)
        tester["quotes"] = [q.strip() for q in quotes if q.strip()]

        # Extract interpretation
        read_match = re.search(r'### Your read\s*(.*?)(?=\n---|\Z)', section, re.DOTALL)
        if read_match:
            tester["interpretation"] = read_match.group(1).strip()

        # Only include testers with actual data
        has_data = tester["name"] or any(v for v in tester["responses"].values())
        if has_data:
            testers.append(tester)

    return testers


def extract_themes(testers: list[dict]) -> dict:
    """Extract and count themes across all testers."""
    themes = {
        "ux_blockers": [],       # From stuck/confused + stuck_points
        "missing_features": [],  # From expected_not_happened
        "priority_changes": [],  # From first_change
        "core_value": [],        # From would_use
        "revenue_signals": [],   # From would_pay
    }

    for i, tester in enumerate(testers, 1):
        tid = tester["name"] or f"Tester {i}"

        if tester["stuck_points"]:
            themes["ux_blockers"].append({
                "tester": tid,
                "feedback": tester["stuck_points"]
            })
        if tester["responses"]["stuck_confused"]:
            themes["ux_blockers"].append({
                "tester": tid,
                "feedback": tester["responses"]["stuck_confused"]
            })
        if tester["responses"]["expected_not_happened"]:
            themes["missing_features"].append({
                "tester": tid,
                "feedback": tester["responses"]["expected_not_happened"]
            })
        if tester["responses"]["first_change"]:
            themes["priority_changes"].append({
                "tester": tid,
                "feedback": tester["responses"]["first_change"]
            })
        if tester["responses"]["would_use"]:
            themes["core_value"].append({
                "tester": tid,
                "feedback": tester["responses"]["would_use"]
            })
        if tester["responses"]["would_pay"]:
            themes["revenue_signals"].append({
                "tester": tid,
                "feedback": tester["responses"]["would_pay"]
            })

    return themes


def build_analysis(testers: list[dict], themes: dict) -> dict:
    """Build the final analysis output."""
    total_testers = len(testers)
    completed = sum(1 for t in testers if t["test_completed"] in ["yes", "y"])
    partial = sum(1 for t in testers if t["test_completed"] in ["partial", "p"])
    not_completed = total_testers - completed - partial

    # Completion signals
    completion = {
        "total_testers": total_testers,
        "completed_test": completed,
        "partial_test": partial,
        "did_not_complete": not_completed,
        "completion_rate": f"{(completed / total_testers * 100):.0f}%" if total_testers > 0 else "0%",
    }

    # Aggregate quotes
    all_quotes = []
    for t in testers:
        for q in t["quotes"]:
            all_quotes.append({"tester": t["name"] or "anonymous", "quote": q})

    # Core value verdict
    positive_signals = sum(
        1 for t in testers
        if t["responses"]["would_use"] and
        any(word in t["responses"]["would_use"].lower() for word in ["yes", "definitely", "absolutely", "would", "already"])
    )
    negative_signals = sum(
        1 for t in testers
        if t["responses"]["would_use"] and
        any(word in t["responses"]["would_use"].lower() for word in ["no", "not", "wouldn't", "don't think"])
    )

    core_value_verdict = "unclear"
    if total_testers >= 3:
        if positive_signals >= total_testers * 0.6:
            core_value_verdict = "positive — most testers would use this"
        elif negative_signals >= total_testers * 0.6:
            core_value_verdict = "negative — most testers would not use this"
        else:
            core_value_verdict = "mixed — no clear signal, may need more testers or a pivot"

    # Revenue verdict
    pay_signals = sum(
        1 for t in testers
        if t["responses"]["would_pay"] and t["responses"]["would_pay"].strip()
    )

    analysis = {
        "meta": {
            "total_testers": total_testers,
            "minimum_for_patterns": 3,
            "confidence": "high" if total_testers >= 5 else "medium" if total_testers >= 3 else "low",
            "warning": None if total_testers >= 3 else f"Only {total_testers} testers — patterns are directional, not validated. Get {3 - total_testers} more.",
        },
        "completion": completion,
        "themes": {
            category: {
                "count": len(items),
                "testers": [item["tester"] for item in items],
                "feedback": [item["feedback"] for item in items],
                "action": "SPEC IT" if len(items) >= 3 else "NOTE IT" if len(items) >= 2 else "IGNORE",
            }
            for category, items in themes.items()
        },
        "verdicts": {
            "core_value": core_value_verdict,
            "revenue_potential": f"{pay_signals}/{total_testers} testers indicated willingness to pay",
        },
        "quotes": all_quotes,
    }

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Analyze feedback log and extract patterns")
    parser.add_argument("feedback_log", help="Path to the feedback log markdown file")
    parser.add_argument("--output", "-o", default=None, help="Output path for analysis JSON (default: stdout)")
    args = parser.parse_args()

    log_path = Path(args.feedback_log)
    if not log_path.exists():
        print(f"Error: Feedback log not found at {log_path}", file=sys.stderr)
        sys.exit(1)

    content = log_path.read_text(encoding="utf-8")
    testers = parse_feedback_log(content)

    if not testers:
        print("Error: No tester data found in the feedback log. Make sure sections are filled in.", file=sys.stderr)
        sys.exit(1)

    themes = extract_themes(testers)
    analysis = build_analysis(testers, themes)

    output_json = json.dumps(analysis, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"Analysis written to {output_path}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
