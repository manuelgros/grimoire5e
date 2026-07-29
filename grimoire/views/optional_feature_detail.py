from typing import Any, Dict, List

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Button, Static

from ..models import OptionalFeature
from ..services import SOURCE_FULL
from .feature_detail_base import FeatureDetailScreen


def _pluralize(name: str, amount: int) -> str:
    if amount <= 1:
        return name
    if name.endswith("Die"):
        return f"{name[:-3]}Dice"
    return f"{name}s"


class OptionalFeatureDetailScreen(FeatureDetailScreen):
    """Detail screen for a single optional feature (Fighting Style, Invocation, ...)."""

    def __init__(self, feature: OptionalFeature) -> None:
        super().__init__()
        self.feature = feature

    def compose(self) -> ComposeResult:
        of = self.feature

        with Vertical():
            yield Static(f"[bold]{of.name}[/bold]", classes="title")
            if of.feature_types:
                yield Static(f"[bold]{of.feature_type_display}[/bold]")
            if of.is_variant:
                yield Static("[dim]Optional / Variant Feature[/dim]")
            if of.has_prerequisite:
                yield self._stat("Prerequisite:", self._format_prereq(of.prerequisite or []))
            if of.consumes:
                yield self._stat("Cost:", self._format_consumes(of.consumes))
            yield Static("")

            with ScrollableContainer():
                if of.entries:
                    yield from self._compose_entries(of.entries)
                yield Static(f"\n[dim]Source: {SOURCE_FULL.get(of.source, of.source)}[/dim]")

            yield Button("Back", id="back")

    def _format_consumes(self, consumes: Dict[str, Any]) -> str:
        name = str(consumes.get("name", "")).strip()
        amount = consumes.get("amount")
        if not name:
            return "—"
        if isinstance(amount, int):
            return f"{amount} {_pluralize(name, amount)}"
        return name

    def _format_prereq(self, prereqs: List[Any]) -> str:
        parts = []
        for prereq in prereqs:
            if not isinstance(prereq, dict):
                parts.append(self._strip_tags(str(prereq)))
                continue
            for key, val in prereq.items():
                if key == "level":
                    parts.append(self._format_level_prereq(val))
                elif key == "pact":
                    parts.append(f"Pact of the {val}")
                elif key == "patron":
                    parts.append(f"{val} patron")
                elif key == "spell":
                    spells = [self._format_spell_prereq(s) for s in val]
                    parts.append(" or ".join(s for s in spells if s))
                elif key == "optionalfeature":
                    names = [str(o).split("|")[0].title() for o in val]
                    parts.append(" or ".join(names))
                elif key == "feat":
                    names = [str(f_).split("|")[0].title() for f_ in val]
                    parts.append(", ".join(names) + " feat")
                elif key == "item":
                    items = val if isinstance(val, list) else [val]
                    parts.append(", ".join(self._strip_tags(str(i)) for i in items))
                elif key == "otherSummary":
                    if isinstance(val, dict):
                        text = val.get("entrySummary") or val.get("entry") or ""
                    else:
                        text = str(val)
                    parts.append(self._strip_tags(str(text)))
                elif key == "other":
                    parts.append(self._strip_tags(str(val)))
        return ", ".join(p for p in parts if p) or "None"

    def _format_level_prereq(self, val: Any) -> str:
        """Level prerequisites are either a bare number or a level within a class."""
        if isinstance(val, dict):
            level = val.get("level", "")
            class_info = val.get("class") or {}
            class_name = class_info.get("name") if isinstance(class_info, dict) else class_info
            subclass = val.get("subclass") or {}
            sub_name = subclass.get("name") if isinstance(subclass, dict) else subclass
            who = " ".join(str(n) for n in (class_name, sub_name) if n)
            return f"Level {level} {who}".strip() if who else f"Level {level}"
        return f"Level {val}"

    def _format_spell_prereq(self, raw: Any) -> str:
        """Spell prerequisites use a '#c' suffix to mean the spell must be a cantrip."""
        text = str(raw)
        suffix = ""
        if "#c" in text:
            text = text.replace("#c", "")
            suffix = " cantrip"
        return f"{text.split('|')[0]}{suffix}"
