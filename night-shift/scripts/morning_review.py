#!/usr/bin/env python3
"""
Morning review: analyze overnight autonomous run results.

Usage:
    python morning_review.py --since "8 hours ago"
    python morning_review.py --since "2026-04-07 23:00" --allowed-scope /app/responses /components/mobile

Reads git history, commits, and progress files from the overnight run.
Categorizes the outcome as SHIPPED, PARTIAL, STUCK, or DRIFTED.
Outputs a structured JSON report the agent uses to generate the morning briefing.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from collections import Counter


def run_cmd(cmd, cwd=None, timeout=60):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1


def get_commits_since(cwd, since):
    """Get commits since the given time."""
    fmt = '--pretty=format:%H|%an|%at|%s'
    stdout, _, rc = run_cmd(f'git log {fmt} --since="{since}"', cwd=cwd)
    if rc != 0 or not stdout:
        return []
    commits = []
    for line in stdout.split('\n'):
        parts = line.split('|', 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "timestamp": int(parts[2]),
                "message": parts[3],
            })
    return commits


def get_files_changed(cwd, since):
    """Get all files changed since the given time."""
    stdout, _, rc = run_cmd(f'git log --name-only --pretty=format: --since="{since}"', cwd=cwd)
    if rc != 0:
        return []
    files = set()
    for line in stdout.split('\n'):
        line = line.strip()
        if line and not line.startswith('commit '):
            files.add(line)
    return sorted(files)


def check_scope_violations(files_changed, allowed_scope):
    """Check if any modified files are outside the allowed scope."""
    if not allowed_scope:
        return []
    violations = []
    for f in files_changed:
        if not any(f.startswith(scope.lstrip('/')) for scope in allowed_scope):
            violations.append(f)
    return violations


def detect_test_runner(cwd):
    pkg_path = Path(cwd) / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            if "test" in pkg.get("scripts", {}):
                return "npm test"
        except Exception:
            pass
    if (Path(cwd) / "pytest.ini").exists() or (Path(cwd) / "pyproject.toml").exists():
        return "pytest"
    return None


def run_tests(cwd):
    """Run tests and return pass/fail with details."""
    runner = detect_test_runner(cwd)
    if not runner:
        return {"ran": False, "reason": "No test runner detected"}
    stdout, stderr, rc = run_cmd(runner, cwd=cwd, timeout=300)
    return {
        "ran": True,
        "runner": runner,
        "passed": rc == 0,
        "output_tail": (stdout + "\n" + stderr).split('\n')[-10:],
    }


def parse_progress_file(cwd):
    """Read Ralph's progress.txt if it exists."""
    paths = [
        Path(cwd) / "progress.txt",
        Path(cwd) / ".night-shift" / "progress.txt",
        Path(cwd) / "scripts" / "ralph" / "progress.txt",
    ]
    for p in paths:
        if p.exists():
            try:
                return p.read_text()
            except Exception:
                pass
    return None


def detect_stuck_pattern(commits):
    """Detect if the agent was stuck in a loop."""
    if len(commits) < 3:
        return False
    # Look for near-duplicate commit messages
    messages = [c["message"].lower() for c in commits]
    msg_counter = Counter(messages)
    for msg, count in msg_counter.items():
        if count >= 3:
            return True
    # Look for fix/revert/retry patterns
    fix_keywords = ["fix", "retry", "attempt", "revert", "undo"]
    fix_count = sum(1 for m in messages if any(k in m for k in fix_keywords))
    if fix_count > len(messages) * 0.5:
        return True
    return False


def detect_iteration_count(cwd):
    """Read prd.json to see how many iterations actually ran."""
    paths = [
        Path(cwd) / "prd.json",
        Path(cwd) / ".night-shift" / "prd.json",
    ]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                stories = data.get("userStories", [])
                completed = sum(1 for s in stories if s.get("passes"))
                return {
                    "total_stories": len(stories),
                    "completed": completed,
                    "failed": len(stories) - completed,
                }
            except Exception:
                pass
    return None


def categorize_outcome(commits, files_changed, violations, test_result, stuck, iteration_data):
    """Classify the run into one of four outcomes."""
    
    # DRIFTED: scope violations found
    if violations:
        return {
            "outcome": "DRIFTED",
            "emoji": "🚨",
            "summary": f"Agent modified {len(violations)} files outside allowed scope. RESET RECOMMENDED.",
            "action": "git reset --hard to the pre-sleep checkpoint. Do not salvage commits.",
        }
    
    # STUCK: repeated patterns, few commits, stuck loop
    if stuck or (len(commits) > 0 and len(commits) < 3):
        return {
            "outcome": "STUCK",
            "emoji": "🔄",
            "summary": f"Loop appears stuck. Only {len(commits)} commits, possibly in a retry loop.",
            "action": "Review progress.txt to see what blocked the agent. Fix the spec ambiguity. Try again tonight.",
        }
    
    # Check spec completion
    if iteration_data:
        if iteration_data["completed"] == iteration_data["total_stories"] and test_result.get("passed"):
            return {
                "outcome": "SHIPPED",
                "emoji": "✅",
                "summary": f"All {iteration_data['total_stories']} specs completed. Tests passing.",
                "action": "Review completed work. Deploy (Issue 07).",
            }
        elif iteration_data["completed"] > 0:
            return {
                "outcome": "PARTIAL",
                "emoji": "⚠️",
                "summary": f"{iteration_data['completed']}/{iteration_data['total_stories']} specs completed. " +
                          ("Tests passing." if test_result.get("passed") else "Tests failing."),
                "action": "Merge completed specs. Revert failed ones. Rewrite failed specs with tighter definitions.",
            }
    
    # Fallback based on test state
    if test_result.get("passed") and len(commits) > 3:
        return {
            "outcome": "SHIPPED",
            "emoji": "✅",
            "summary": f"{len(commits)} commits, tests passing. Manual spec verification needed.",
            "action": "Verify each spec's acceptance criteria manually. Deploy when confirmed.",
        }
    if not test_result.get("passed"):
        return {
            "outcome": "PARTIAL",
            "emoji": "⚠️",
            "summary": f"{len(commits)} commits made but tests failing.",
            "action": "Review which tests fail. Revert or fix manually.",
        }
    
    return {
        "outcome": "UNKNOWN",
        "emoji": "❓",
        "summary": f"{len(commits)} commits made. Unable to auto-classify.",
        "action": "Manual review required.",
    }


def main():
    parser = argparse.ArgumentParser(description="Review overnight autonomous run results")
    parser.add_argument("--since", default="8 hours ago", help="Time range for git log")
    parser.add_argument("--cwd", default=".", help="Project directory")
    parser.add_argument("--allowed-scope", nargs="*", default=[], help="Allowed file path prefixes")
    parser.add_argument("--run-tests", action="store_true", help="Run test suite for current status")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()

    report = {
        "cwd": str(cwd),
        "since": args.since,
        "commits": [],
        "files_changed": [],
        "scope_violations": [],
        "tests": {},
        "progress_file": None,
        "iteration_data": None,
        "stuck_pattern": False,
        "outcome": {},
    }

    # Gather data
    commits = get_commits_since(cwd, args.since)
    report["commits"] = commits
    report["commit_count"] = len(commits)

    if not commits:
        report["outcome"] = {
            "outcome": "NO_RUN",
            "emoji": "❌",
            "summary": "No commits found in the specified time range. The loop may not have run.",
            "action": "Check if the loop actually started. Review /.night-shift/ logs if present.",
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0)

    files_changed = get_files_changed(cwd, args.since)
    report["files_changed"] = files_changed
    report["files_changed_count"] = len(files_changed)

    violations = check_scope_violations(files_changed, args.allowed_scope)
    report["scope_violations"] = violations

    if args.run_tests:
        report["tests"] = run_tests(cwd)

    progress = parse_progress_file(cwd)
    if progress:
        report["progress_file"] = {
            "exists": True,
            "lines": len(progress.split('\n')),
            "last_20_lines": progress.split('\n')[-20:],
        }

    report["iteration_data"] = detect_iteration_count(cwd)
    report["stuck_pattern"] = detect_stuck_pattern(commits)

    # Categorize
    report["outcome"] = categorize_outcome(
        commits,
        files_changed,
        violations,
        report["tests"],
        report["stuck_pattern"],
        report["iteration_data"],
    )

    # Timeline summary (commits grouped by hour)
    if commits:
        import datetime
        timeline = []
        for c in commits:
            dt = datetime.datetime.fromtimestamp(c["timestamp"])
            timeline.append({
                "time": dt.strftime("%H:%M"),
                "hash": c["hash"][:8],
                "message": c["message"][:80],
            })
        report["timeline"] = sorted(timeline, key=lambda x: x["time"])

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
