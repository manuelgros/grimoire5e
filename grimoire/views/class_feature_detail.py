import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from ..models import ClassFeature
from ..services import SOURCE_FULL, SOURCE_SHORT
from ..themes import THEME_LABEL_COLORS, _DEFAULT_LABEL_COLOR


class ClassFeatureDetailScreen(Screen):
    """Detail screen for a single class or subclass feature."""

    def __init__(self, feature: ClassFeature) -> None:
        super().__init__()
        self.feature = feature
        self._refs: Dict[str, Tuple[str, str]] = {}

    def _label_color(self) -> str:
        return THEME_LABEL_COLORS.get(self.app.theme, _DEFAULT_LABEL_COLOR)

    def _stat(self, label: str, value: str) -> Static:
        t = Text()
        t.append(label, style=f"bold {self._label_color()}")
        t.append(f" {value}")
        return Static(t)

    def compose(self) -> ComposeResult:
        cf = self.feature
        class_full = f"{cf.class_name} ({SOURCE_SHORT.get(cf.class_source, cf.class_source)})"

        with Vertical():
            yield Static(f"[bold]{cf.name}[/bold]", classes="title")
            if cf.is_variant:
                yield Static("[dim]Optional / Variant Feature[/dim]")
            yield self._stat("Class:", class_full)
            yield self._stat("Level:", str(cf.level))
            if cf.is_subclass and cf.subclass_display:
                sub_src = cf.subclass_source or ""
                yield self._stat(
                    "Subclass:",
                    f"{cf.subclass_display} ({sub_src})" if sub_src else cf.subclass_display,
                )
            yield Static("")

            with ScrollableContainer():
                if cf.entries:
                    yield from self._compose_entries(cf.entries)
                yield Static(f"\n[dim]Source: {SOURCE_FULL.get(cf.source, cf.source)}[/dim]")

            yield Button("Back", id="back")

    def _compose_entries(self, entries: List[Any]) -> Iterator[Any]:
        """Yield widgets for entries, turning top-level refs into navigable buttons."""
        buffer: List[Any] = []

        def flush_buffer() -> Iterator[Any]:
            if buffer:
                yield Static(self._format_entries(buffer))
                yield Static("")
                buffer.clear()

        for entry in entries:
            ref_info = self._extract_ref(entry)
            if ref_info is not None:
                yield from flush_buffer()
                ref_type, ref_str = ref_info
                name = ref_str.split("|")[0] if ref_str else "(unknown)"
                button_id = f"ref_{len(self._refs)}"
                self._refs[button_id] = (ref_type, ref_str)
                yield Button(f"→ {name}", id=button_id, classes="ref-link")
            else:
                buffer.append(entry)
        yield from flush_buffer()

    @staticmethod
    def _extract_ref(entry: Any) -> Optional[Tuple[str, str]]:
        if not isinstance(entry, dict):
            return None
        t = entry.get("type")
        if t == "refClassFeature":
            return ("refClassFeature", entry.get("classFeature") or "")
        if t == "refSubclassFeature":
            return ("refSubclassFeature", entry.get("subclassFeature") or "")
        return None

    def _resolve_ref(self, ref_type: str, ref_str: str) -> Optional[ClassFeature]:
        if not ref_str:
            return None
        parts = ref_str.split("|")
        features = self.app.data_loader.classfeatures

        if ref_type == "refClassFeature" and len(parts) >= 4:
            name = parts[0]
            class_name = parts[1]
            class_source = parts[2] or "PHB"
            try:
                level = int(parts[3])
            except ValueError:
                return None
            feature_source = parts[4] if len(parts) > 4 and parts[4] else class_source
            for cf in features:
                if (
                    cf.name == name
                    and cf.class_name == class_name
                    and cf.class_source == class_source
                    and cf.level == level
                    and cf.source == feature_source
                    and not cf.is_subclass
                ):
                    return cf
            return None

        if ref_type == "refSubclassFeature" and len(parts) >= 6:
            name = parts[0]
            class_name = parts[1]
            class_source = parts[2] or "PHB"
            sub_short = parts[3]
            sub_source = parts[4] or class_source
            try:
                level = int(parts[5])
            except ValueError:
                return None
            feature_source = parts[6] if len(parts) > 6 and parts[6] else sub_source
            for cf in features:
                if (
                    cf.name == name
                    and cf.class_name == class_name
                    and cf.class_source == class_source
                    and cf.subclass_short_name == sub_short
                    and cf.subclass_source == sub_source
                    and cf.level == level
                    and cf.source == feature_source
                    and cf.is_subclass
                ):
                    return cf
            return None

        return None

    def _strip_tags(self, text: str) -> str:
        text = re.sub(r"\{@action ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@condition ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@item ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@spell ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@creature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@feat ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@classFeature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@subclassFeature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@skill ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@damage ([^}]+)\}", r"\1", text)
        text = re.sub(r"\{@dice ([^}]+)\}", r"\1", text)
        text = re.sub(r"\{@dc ([^}]+)\}", r"DC \1", text)
        text = re.sub(r"\{@hit ([^}]+)\}", r"+\1", text)
        text = re.sub(r"\{@h\}", "", text)
        text = re.sub(r"\{@\w+ ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        return text.strip()

    def _format_entries(self, entries: List[Any]) -> str:
        lc = self._label_color()

        def render(entry: Any) -> str:
            if isinstance(entry, str):
                return self._strip_tags(entry)
            if isinstance(entry, dict):
                e_type = entry.get("type")
                if e_type == "list":
                    return "\n".join(f"- {render(e)}" for e in entry.get("items", []))
                if e_type == "item":
                    name = entry.get("name", "")
                    if "entries" in entry:
                        body = "\n".join(render(e) for e in entry["entries"])
                    else:
                        raw = entry.get("entry", "")
                        body = self._strip_tags(raw) if isinstance(raw, str) else render(raw)
                    return f"[bold {lc}]{name}.[/bold {lc}] {body}" if name else body
                if e_type in {"entries", "section"}:
                    header = entry.get("name")
                    body = "\n".join(render(e) for e in entry.get("entries", []))
                    return f"[bold {lc}]{header}[/bold {lc}]\n{body}" if header else body
                if e_type == "table":
                    title = entry.get("caption", "")
                    rows = entry.get("rows", [])
                    lines = [f"[bold {lc}]{title}[/bold {lc}]"] if title else []
                    for row in rows:
                        cells = [self._strip_tags(str(c)) if isinstance(c, str) else str(c) for c in row]
                        lines.append(" | ".join(cells))
                    return "\n".join(lines)
                if e_type in {"refClassFeature", "refSubclassFeature", "refOptionalfeature"}:
                    ref = entry.get("classFeature") or entry.get("subclassFeature") or entry.get("optionalfeature") or ""
                    name = ref.split("|")[0] if isinstance(ref, str) else str(ref)
                    return f"[dim]→ {name}[/dim]"
                if "entries" in entry:
                    return "\n".join(render(e) for e in entry["entries"])
                if "entry" in entry:
                    raw = entry["entry"]
                    return self._strip_tags(raw) if isinstance(raw, str) else render(raw)
                return str(entry)
            if isinstance(entry, list):
                return "\n".join(render(e) for e in entry)
            return str(entry)

        return "\n\n".join(render(e) for e in entries)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            while len(self.app.screen_stack) > 1 and isinstance(
                self.app.screen_stack[-1], ClassFeatureDetailScreen
            ):
                self.app.pop_screen()
            self.app.action_focus_search()
            event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.app.pop_screen()
            return
        if button_id in self._refs:
            ref_type, ref_str = self._refs[button_id]
            target = self._resolve_ref(ref_type, ref_str)
            if target is not None:
                self.app.push_screen(ClassFeatureDetailScreen(target))
            else:
                name = ref_str.split("|")[0] if ref_str else "feature"
                self.app.notify(
                    f"Could not find '{name}' — the source may not be installed.",
                    severity="warning",
                )
