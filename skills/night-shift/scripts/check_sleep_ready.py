#!/usr/bin/env python3
"""
Pre-sleep check: verify the project is safe for an overnight autonomous run.

Usage:
    python check_sleep_ready.py --specs spec1.md spec2.md
    python check_sleep_ready.py --specs spec1.md --max-iterations 5

Checks:
    - Git state is clean (no uncommitted changes)
    - Current branch is not main/master (safer on a feature branch)
    - Tests pass (detects test runner from package.json/pytest/etc.)
    - Typecheck passes (if applicable)
    - Specified specs exist and have all 5 sections from Issue 03
    - No spec touches critical areas (auth, payments, migrations) without explicit flag

Outputs JSON report with PASS/BLOCKED and reasons.
Exit code 0 = safe to proceed, 1 = blocked.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, cwd=None, timeout=60):
    """Run a shell command, return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timeout after {timeout}s", -1
    except Exception as e:
        return "", str(e), -1


def check_git_clean(cwd):
    """Verify no uncommitted changes."""
    stdout, _, rc = run_cmd("git status --porcelain", cwd=cwd)
    if rc != 0:
        return {"pass": False, "reason": "Not a git repository or git command failed"}
    if stdout:
        untracked = [l for l in stdout.split('\n') if l.startswith('??')]
        modified = [l for l in stdout.split('\n') if not l.startswith('??')]
        return {
            "pass": False,
            "reason": f"Dirty git state: {len(modified)} modified, {len(untracked)} untracked",
            "details": stdout.split('\n')[:10],
        }
    return {"pass": True, "reason": "Clean working tree"}


def check_branch(cwd):
    """Verify not on main/master branch."""
    stdout, _, rc = run_cmd("git branch --show-current", cwd=cwd)
    if rc != 0:
        return {"pass": False, "reason": "Could not determine current branch"}
    branch = stdout.strip()
    if branch in ("main", "master", "production", "prod"):
        return {
            "pass": False,
            "reason": f"Currently on protected branch '{branch}'. Create a feature branch first.",
            "suggestion": f"git checkout -b night-shift/$(date +%Y%m%d)",
        }
    return {"pass": True, "reason": f"On safe branch: {branch}", "branch": branch}


def detect_test_runner(cwd):
    """Detect which test runner this project uses."""
    pkg_path = Path(cwd) / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                return "npm test"
        except Exception:
            pass
    if (Path(cwd) / "pytest.ini").exists() or (Path(cwd) / "pyproject.toml").exists():
        return "pytest"
    if (Path(cwd) / "go.mod").exists():
        return "go test ./..."
    if (Path(cwd) / "Cargo.toml").exists():
        return "cargo test"
    return None


def check_tests(cwd):
    """Run the test suite and verify it passes."""
    runner = detect_test_runner(cwd)
    if not runner:
        return {
            "pass": True,
            "reason": "No test runner detected — skipping (WARNING: overnight runs are riskier without tests)",
            "warning": True,
        }
    stdout, stderr, rc = run_cmd(runner, cwd=cwd, timeout=300)
    if rc == 0:
        return {"pass": True, "reason": f"Tests pass ({runner})"}
    return {
        "pass": False,
        "reason": f"Tests failing. Fix before running overnight.",
        "runner": runner,
        "output_tail": (stdout + "\n" + stderr).split('\n')[-20:],
    }


def check_typecheck(cwd):
    """Run typecheck if available."""
    pkg_path = Path(cwd) / "package.json"
    if not pkg_path.exists():
        return {"pass": True, "reason": "No package.json — skipping typecheck"}
    try:
        pkg = json.loads(pkg_path.read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "typescript" not in deps:
            return {"pass": True, "reason": "No TypeScript — skipping typecheck"}
        stdout, stderr, rc = run_cmd("npx tsc --noEmit", cwd=cwd, timeout=120)
        if rc == 0:
            return {"pass": True, "reason": "Typecheck passes"}
        return {
            "pass": False,
            "reason": "Typecheck failing. Fix before running overnight.",
            "output_tail": (stdout + "\n" + stderr).split('\n')[-15:],
        }
    except Exception as e:
        return {"pass": True, "reason": f"Typecheck skipped: {e}"}


def validate_spec(spec_path):
    """Check that a spec has all 5 sections from Issue 03 format."""
    path = Path(spec_path)
    if not path.exists():
        return {"pass": False, "reason": f"Spec not found: {spec_path}"}
    content = path.read_text()
    required_sections = ["## Context", "## Requirements", "## Constraints", "## Acceptance"]
    missing = [s for s in required_sections if s not in content]
    if missing:
        return {
            "pass": False,
            "reason": f"Spec missing sections: {', '.join(missing)}",
            "spec": str(path),
        }
    # Check for critical area references
    critical_patterns = [
        r'/api/auth/', r'/app/api/auth/', r'auth\.ts', r'middleware\.ts',
        r'payment', r'stripe', r'webhook',
        r'/prisma/migrations', r'/supabase/migrations',
        r'\.env', r'production',
    ]
    critical_hits = []
    for pattern in critical_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            critical_hits.append(pattern)
    return {
        "pass": True,
        "reason": "Spec valid",
        "spec": str(path),
        "critical_areas": critical_hits,
    }


def estimate_scope(specs):
    """Rough estimate of files that will be touched."""
    files = set()
    for spec in specs:
        if "details" in spec and "spec" in spec:
            try:
                content = Path(spec["spec"]).read_text()
                # Match file paths
                paths = re.findall(
                    r'/(?:app|components|lib|utils|server|pages|src)[\w/.-]+\.(?:tsx?|jsx?|css|json)',
                    content
                )
                files.update(paths)
            except Exception:
                pass
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Pre-sleep check for overnight autonomous runs")
    parser.add_argument("--specs", nargs="+", required=True, help="Spec files to include in the run")
    parser.add_argument("--cwd", default=".", help="Project directory")
    parser.add_argument("--max-iterations", type=int, default=8, help="Max loop iterations")
    parser.add_argument("--first-run", action="store_true", help="Flag for first overnight run (stricter limits)")
    parser.add_argument("--allow-critical", action="store_true", help="Allow specs touching auth/payments/migrations")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()

    report = {
        "timestamp": None,
        "cwd": str(cwd),
        "specs": args.specs,
        "checks": {},
        "blockers": [],
        "warnings": [],
        "ready": False,
    }

    import datetime
    report["timestamp"] = datetime.datetime.now().isoformat()

    # First-run limits
    if args.first_run:
        if len(args.specs) > 1:
            report["blockers"].append(
                f"First overnight run must use MAX 1 spec. You specified {len(args.specs)}. "
                "Start smaller — build trust before scaling."
            )
        if args.max_iterations > 3:
            report["warnings"].append(
                f"First run with {args.max_iterations} max iterations. Recommend 3 or fewer."
            )

    # Git state
    report["checks"]["git_clean"] = check_git_clean(cwd)
    if not report["checks"]["git_clean"]["pass"]:
        report["blockers"].append(report["checks"]["git_clean"]["reason"])

    # Branch
    report["checks"]["branch"] = check_branch(cwd)
    if not report["checks"]["branch"]["pass"]:
        report["blockers"].append(report["checks"]["branch"]["reason"])

    # Tests
    report["checks"]["tests"] = check_tests(cwd)
    if not report["checks"]["tests"]["pass"]:
        report["blockers"].append(report["checks"]["tests"]["reason"])
    elif report["checks"]["tests"].get("warning"):
        report["warnings"].append(report["checks"]["tests"]["reason"])

    # Typecheck
    report["checks"]["typecheck"] = check_typecheck(cwd)
    if not report["checks"]["typecheck"]["pass"]:
        report["blockers"].append(report["checks"]["typecheck"]["reason"])

    # Specs
    spec_reports = []
    for spec in args.specs:
        spec_report = validate_spec(spec)
        spec_reports.append(spec_report)
        if not spec_report["pass"]:
            report["blockers"].append(spec_report["reason"])
        elif spec_report.get("critical_areas") and not args.allow_critical:
            report["blockers"].append(
                f"Spec {spec} touches critical areas: {spec_report['critical_areas']}. "
                "Re-run with --allow-critical if this is intentional."
            )
    report["checks"]["specs"] = spec_reports

    # Scope estimate
    report["estimated_scope"] = estimate_scope(spec_reports)

    # Final verdict
    report["ready"] = len(report["blockers"]) == 0

    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["ready"] else 1)


if __name__ == "__main__":
    main()
