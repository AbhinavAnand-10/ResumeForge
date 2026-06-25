"""
Diff engine — compares original and optimized resume text line-by-line
and returns structured DiffLine objects for the frontend viewer.
"""
from __future__ import annotations

import difflib
from app.models.schemas import DiffLine


def compute_diff(original: str, optimized: str) -> list[DiffLine]:
    """
    Produce a structured line-level diff between original and optimized text.
    Uses Python's SequenceMatcher for a clean unified diff.
    """
    orig_lines = original.splitlines()
    opt_lines = optimized.splitlines()

    matcher = difflib.SequenceMatcher(None, orig_lines, opt_lines, autojunk=False)
    result: list[DiffLine] = []
    line_no = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for orig, opt in zip(orig_lines[i1:i2], opt_lines[j1:j2]):
                result.append(DiffLine(
                    line_no=line_no,
                    original=orig,
                    optimized=opt,
                    change_type="unchanged",
                ))
                line_no += 1

        elif tag == "replace":
            orig_chunk = orig_lines[i1:i2]
            opt_chunk = opt_lines[j1:j2]
            # Pair up lines; pad whichever side is shorter
            max_len = max(len(orig_chunk), len(opt_chunk))
            for k in range(max_len):
                orig_line = orig_chunk[k] if k < len(orig_chunk) else ""
                opt_line = opt_chunk[k] if k < len(opt_chunk) else ""
                result.append(DiffLine(
                    line_no=line_no,
                    original=orig_line,
                    optimized=opt_line,
                    change_type="modified",
                    reason="Rephrased for ATS keyword density and impact",
                ))
                line_no += 1

        elif tag == "delete":
            for orig in orig_lines[i1:i2]:
                result.append(DiffLine(
                    line_no=line_no,
                    original=orig,
                    optimized="",
                    change_type="removed",
                    reason="Removed: generic/fluffy phrase",
                ))
                line_no += 1

        elif tag == "insert":
            for opt in opt_lines[j1:j2]:
                result.append(DiffLine(
                    line_no=line_no,
                    original="",
                    optimized=opt,
                    change_type="added",
                    reason="Added: missing keyword or structural element",
                ))
                line_no += 1

    return result


def diff_stats(diff_lines: list[DiffLine]) -> dict:
    """Return a quick summary count of each change type."""
    counts: dict[str, int] = {"unchanged": 0, "modified": 0, "added": 0, "removed": 0}
    for line in diff_lines:
        counts[line.change_type] = counts.get(line.change_type, 0) + 1
    total = sum(counts.values())
    changed = total - counts["unchanged"]
    return {
        **counts,
        "total_lines": total,
        "total_changed": changed,
        "change_percent": round(changed / total * 100, 1) if total else 0,
    }
