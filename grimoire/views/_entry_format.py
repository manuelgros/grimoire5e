"""Shared renderers for 5etools entry structures."""

from typing import Any, Callable, List, Optional

RULE_MAX_WIDTH = 60

# Renderer.dice.POS_INFINITE in the 5etools source — used as the max of an
# open-ended roll range, rendered as "N+" rather than "N-100000000000000000000".
_POS_INFINITE = 100000000000000000000


_ATTR_FULL = {
    "str": "Strength", "dex": "Dexterity", "con": "Constitution",
    "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma",
}


def format_attributes(attributes: List[str]) -> str:
    """
    Mirror Parser.attrChooseToFull in the 5etools source: one attribute reads
    "Intelligence modifier", several read "Strength or Dexterity modifier
    (your choice)".
    """
    if len(attributes) == 1:
        attr = attributes[0]
        if attr == "spellcasting":
            return "spellcasting ability modifier"
        return f"{_ATTR_FULL.get(attr, attr.title())} modifier"
    names = [_ATTR_FULL.get(a, a.title()) for a in attributes]
    return f"{' or '.join(names)} modifier (your choice)"


def format_ability_line(entry: dict, label_color: str) -> str:
    """
    Render `{"type": "abilityDc"}` / `{"type": "abilityAttackMod"}` — the spell
    save DC and attack modifier formulae in class Spellcasting features.

    Uses the 2014 ("classic") phrasing from 5etools' render.js; every entry of
    these types in the data comes from a 2014-era book (PHB, TCE, XGE).
    """
    name = entry.get("name", "")
    attrs = format_attributes(entry.get("attributes", []))
    if entry.get("type") == "abilityDc":
        tail = f"8 + your proficiency bonus + your {attrs}"
        label = f"{name} save DC"
    else:
        tail = f"your proficiency bonus + your {attrs}"
        label = f"{name} attack modifier"
    return f"[bold {label_color}]{label}[/bold {label_color}] = {tail}"


def format_roll_cell(cell: dict, strip: Callable[[str], str]) -> str:
    """
    Render a `{"type": "cell"}` table cell, mirroring Renderer's logic in
    5etools' render.js: an explicit `entry` wins, then an exact roll, then a
    min-max range; `pad` zero-pads each number to two digits.
    """
    roll = cell.get("roll")
    if not isinstance(roll, dict):
        entry = cell.get("entry")
        return strip(entry) if isinstance(entry, str) else ""

    if "entry" in cell:
        entry = cell["entry"]
        return strip(entry) if isinstance(entry, str) else str(entry)

    def num(value: Any) -> str:
        return str(value).zfill(2) if roll.get("pad") else str(value)

    if roll.get("exact") is not None:
        return num(roll["exact"])

    lo = roll.get("displayMin", roll.get("min"))
    hi = roll.get("displayMax", roll.get("max"))
    if hi == _POS_INFINITE:
        return f"{num(lo)}+"
    return f"{num(lo)}-{num(hi)}"


def format_table(
    table: dict,
    strip: Callable[[str], str],
    label_color: str,
    render: Optional[Callable[[Any], str]] = None,
) -> str:
    """
    Render a 5etools `{"type": "table"}` entry as aligned plain text.

    Every column except the last is padded to its widest cell so short leading
    columns (dice ranges, tool names) line up; the final column is left to flow
    and soft-wrap, since table bodies are often full sentences.

    `render` is the caller's own entry renderer. Cells are not always plain text
    or roll objects — some hold a whole nested `{"type": "entries"}` block — so
    anything this function doesn't recognise is handed back to the caller rather
    than stringified into a raw dict.
    """
    def cell(value: Any) -> str:
        if isinstance(value, str):
            return strip(value)
        if isinstance(value, dict):
            if value.get("type") == "cell":
                return format_roll_cell(value, strip)
            # Some cells wrap their text in a plain {"entry": …} object
            entry = value.get("entry")
            if isinstance(entry, str) and "entries" not in value:
                return strip(entry)
        if render is not None and not isinstance(value, (str, int, float)):
            return render(value)
        return str(value)

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
