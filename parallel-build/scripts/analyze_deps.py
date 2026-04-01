#!/usr/bin/env python3
"""
Analyze spec dependencies and generate parallel execution batches.

Usage:
    python analyze_deps.py spec1.md spec2.md spec3.md
    python analyze_deps.py --dir /path/to/specs/

Reads spec files (Issue 03 format), extracts file paths and table references,
detects conflicts between specs, and outputs batched execution plan.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return ""


def extract_file_paths(content: str) -> dict:
    """Extract file paths mentioned in a spec."""
    creates = []
    modifies = []
    reads = []

    # Match common path patterns: /app/..., /components/..., /lib/..., etc.
    path_pattern = r'(?:/(?:app|components|lib|utils|server|pages|src|public|api|hooks|styles|types)[\w/.-]+\.(?:tsx?|jsx?|css|json|md|sql))'
    all_paths = re.findall(path_pattern, content)

    # Check context for create vs modify vs read
    lines = content.split('\n')
    for i, line in enumerate(lines):
        paths_in_line = re.findall(path_pattern, line)
        for p in paths_in_line:
            lower_line = line.lower()
            if any(word in lower_line for word in ['create ', 'new file', 'create/', 'add ']):
                creates.append(p)
            elif any(word in lower_line for word in ['modify', 'update', 'change', 'edit', 'add to', 'add the route']):
                modifies.append(p)
            elif p not in creates and p not in modifies:
                # Default: if in Requirements, likely creates; if in Context, likely reads
                section = get_section(content, i)
                if section == "requirements":
                    creates.append(p)
                elif section == "context":
                    reads.append(p)
                else:
                    reads.append(p)

    return {
        "creates": list(set(creates)),
        "modifies": list(set(modifies)),
        "reads": list(set(reads)),
        "all_touched": list(set(creates + modifies)),
    }


def get_section(content: str, line_idx: int) -> str:
    """Determine which spec section a line belongs to."""
    lines = content.split('\n')
    for i in range(line_idx, -1, -1):
        lower = lines[i].lower().strip()
        if lower.startswith('## context'):
            return "context"
        elif lower.startswith('## requirements'):
            return "requirements"
        elif lower.startswith('## constraints'):
            return "constraints"
        elif lower.startswith('## acceptance'):
            return "acceptance"
        elif lower.startswith('## edge cases'):
            return "edge_cases"
    return "unknown"


def extract_tables(content: str) -> dict:
    """Extract database table references."""
    reads = []
    writes = []

    # Match common table patterns: table_name, `table_name`, 'table_name'
    # Look for patterns like "from TABLE", "insert into TABLE", "update TABLE", "TABLE table"
    table_patterns = [
        (r'(?:from|join|select.*from)\s+[`\']?(\w+)[`\']?\s+(?:table)?', 'reads'),
        (r'(?:insert\s+into|update|delete\s+from)\s+[`\']?(\w+)[`\']?', 'writes'),
        (r'(\w+)\s+table\s*\(', 'writes'),  # "profiles table (id, name, ...)"
        (r'(?:lives?\s+in|stored?\s+in|data\s+in)\s+(?:the\s+)?[`\']?(\w+)[`\']?', 'reads'),
        (r'(?:updates?|saves?\s+to|writes?\s+to|creates?\s+in)\s+(?:the\s+)?[`\']?(\w+)[`\']?', 'writes'),
    ]

    lower_content = content.lower()
    for pattern, action in table_patterns:
        matches = re.findall(pattern, lower_content)
        # Filter out common non-table words
        skip_words = {'the', 'a', 'an', 'this', 'that', 'which', 'from', 'into', 'with',
                      'file', 'page', 'component', 'route', 'function', 'method', 'class',
                      'existing', 'current', 'new', 'each', 'every', 'all', 'any'}
        matches = [m for m in matches if m not in skip_words and len(m) > 2]
        if action == 'reads':
            reads.extend(matches)
        else:
            writes.extend(matches)

    return {
        "reads": list(set(reads)),
        "writes": list(set(writes)),
        "all_touched": list(set(reads + writes)),
    }


def extract_components(content: str) -> list:
    """Extract component references (PascalCase names)."""
    components = re.findall(r'\b([A-Z][a-zA-Z]+(?:Layout|Component|Button|Form|Card|Modal|Page|Input|Select|Toggle|Table|List|Nav|Header|Footer|Sidebar|Provider))\b', content)
    return list(set(components))


def parse_spec(path: Path) -> dict:
    """Parse a spec file and extract its footprint."""
    content = read_file_safe(path)
    if not content:
        return None

    # Extract spec name from title
    title_match = re.search(r'^#\s+(?:Feature|Fix):\s*(.+)', content, re.MULTILINE)
    name = title_match.group(1).strip() if title_match else path.stem

    files = extract_file_paths(content)
    tables = extract_tables(content)
    components = extract_components(content)

    # Estimate complexity
    requirements = re.findall(r'^\d+\.', content, re.MULTILINE)
    complexity = "simple" if len(requirements) <= 3 else "medium" if len(requirements) <= 6 else "complex"
    est_minutes = {"simple": 10, "medium": 18, "complex": 28}[complexity]

    return {
        "name": name,
        "path": str(path),
        "files": files,
        "tables": tables,
        "components": components,
        "complexity": complexity,
        "estimated_minutes": est_minutes,
    }


def find_conflicts(specs: list) -> list:
    """Find conflicts between specs (shared files or tables being modified)."""
    conflicts = []

    for i in range(len(specs)):
        for j in range(i + 1, len(specs)):
            a = specs[i]
            b = specs[j]

            # File conflicts: both create or modify the same file
            shared_files = set(a["files"]["all_touched"]) & set(b["files"]["all_touched"])

            # Table conflicts: both write to the same table
            shared_tables = set(a["tables"]["writes"]) & set(b["tables"]["writes"])

            if shared_files or shared_tables:
                conflicts.append({
                    "spec_a": a["name"],
                    "spec_b": b["name"],
                    "shared_files": list(shared_files),
                    "shared_tables": list(shared_tables),
                    "severity": "high" if shared_files else "medium",
                    "recommendation": "sequential" if shared_files else "monitor",
                })

    return conflicts


def generate_batches(specs: list, conflicts: list) -> list:
    """Generate parallel execution batches avoiding conflicts."""
    # Build conflict graph
    conflict_pairs = set()
    for c in conflicts:
        conflict_pairs.add((c["spec_a"], c["spec_b"]))
        conflict_pairs.add((c["spec_b"], c["spec_a"]))

    batches = []
    remaining = [s["name"] for s in specs]
    spec_map = {s["name"]: s for s in specs}

    while remaining:
        batch = []
        batch_files = set()
        batch_tables = set()

        for name in remaining[:]:
            spec = spec_map[name]

            # Check if this spec conflicts with anything already in the batch
            has_conflict = any((name, b) in conflict_pairs for b in batch)

            # Also check file/table overlap with batch
            spec_files = set(spec["files"]["all_touched"])
            spec_tables = set(spec["tables"]["writes"])
            file_overlap = spec_files & batch_files
            table_overlap = spec_tables & batch_tables

            if not has_conflict and not file_overlap and not table_overlap:
                batch.append(name)
                batch_files.update(spec_files)
                batch_tables.update(spec_tables)

        if not batch:
            # Force add one to prevent infinite loop (no safe parallel option)
            batch.append(remaining[0])

        for name in batch:
            remaining.remove(name)

        batch_specs = [spec_map[n] for n in batch]
        batch_time = max(s["estimated_minutes"] for s in batch_specs) if batch_specs else 0
        sequential_time = sum(s["estimated_minutes"] for s in batch_specs)

        batches.append({
            "batch_number": len(batches) + 1,
            "specs": batch,
            "parallel_count": len(batch),
            "estimated_minutes": batch_time,
            "sequential_minutes": sequential_time,
            "time_saved": sequential_time - batch_time,
        })

    return batches


def main():
    parser = argparse.ArgumentParser(description="Analyze spec dependencies for parallel execution")
    parser.add_argument("specs", nargs="*", help="Spec file paths")
    parser.add_argument("--dir", help="Directory containing spec files")
    parser.add_argument("--output", "-o", help="Output path for analysis JSON")
    args = parser.parse_args()

    # Collect spec paths
    spec_paths = []
    if args.dir:
        dir_path = Path(args.dir)
        spec_paths = sorted(dir_path.glob("*.md"))
    if args.specs:
        spec_paths.extend(Path(p) for p in args.specs)

    if not spec_paths:
        print("Error: No spec files provided. Use --dir or pass file paths.", file=sys.stderr)
        sys.exit(1)

    # Parse all specs
    specs = []
    for path in spec_paths:
        parsed = parse_spec(path)
        if parsed:
            specs.append(parsed)

    if not specs:
        print("Error: No valid specs found.", file=sys.stderr)
        sys.exit(1)

    # Analyze
    conflicts = find_conflicts(specs)
    batches = generate_batches(specs, conflicts)

    total_parallel = sum(b["estimated_minutes"] for b in batches)
    total_sequential = sum(s["estimated_minutes"] for s in specs)

    report = {
        "total_specs": len(specs),
        "specs": specs,
        "conflicts": conflicts,
        "batches": batches,
        "summary": {
            "total_batches": len(batches),
            "parallel_time_minutes": total_parallel,
            "sequential_time_minutes": total_sequential,
            "time_saved_minutes": total_sequential - total_parallel,
            "speedup": f"{total_sequential / total_parallel:.1f}x" if total_parallel > 0 else "N/A",
        },
    }

    output = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Analysis written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
