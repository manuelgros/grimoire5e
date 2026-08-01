"""Shared renderers for 5etools entry structures."""

from typing import Any, Callable, List

RULE_MAX_WIDTH = 60


def format_table(table: dict, strip: Callable[[str], str], label_color: str) -> str:
    """
    Render a 5etools `{"type": "table"}` entry as aligned plain text.

    Every column except the last is padded to its widest cell so short leading
    columns (dice ranges, tool names) line up; the final column is left to flow
    and soft-wrap, since table bodies are often full sentences.
    """
    def cell(value: Any) -> str:
        return strip(value) if isinstance(value, str) else str(value)

    labels = [cell(c) for c in table.get("colLabels", [])]
    rows: List[List[str]] = []
    for raw_row in table.get("rows", []):
        # Skip non-list rows (e.g. {"type": "row"} wrappers) rather than crashing
        if isinstance(raw_row, list):
            rows.append([cell(c) for c in raw_row])

    widths: List[int] = []
    for col in range(max([len(labels)] + [len(r) for r in rows] or [0])):
        candidates = [len(labels[col])] if col < len(labels) else []
        candidates += [len(r[col]) for r in rows if col < len(r)]
        widths.append(max(candidates) if candidates else 0)

    def line(cells: List[str]) -> str:
        out = []
        for i, c in enumerate(cells):
            out.append(c if i == len(cells) - 1 else c.ljust(widths[i]))
        return "  ".join(out).rstrip()

    body = [line(r) for r in rows]

    lines: List[str] = []
    caption = table.get("caption")
    if caption:
        lines.append(f"[bold {label_color}]{cell(caption)}[/bold {label_color}]")
    if labels:
        header = line(labels)
        lines.append(f"[bold]{header}[/bold]")
        # Span the content rather than just the header, which is often much
        # shorter; capped so a column of full sentences doesn't draw a huge rule.
        lines.append("─" * min(max([len(header)] + [len(b) for b in body]), RULE_MAX_WIDTH))
    lines.extend(body)
    return "\n".join(lines)
