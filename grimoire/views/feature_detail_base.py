import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from rich.text import Text
from textual import events
from textual.screen import Screen
from textual.widgets import Button, Static

from ..models import FEATURE_TYPE_LABELS
from ..services import SOURCE_FULL, SOURCE_SHORT
from ..themes import THEME_LABEL_COLORS, _DEFAULT_LABEL_COLOR

# Entry types that point at another feature, and the key holding the reference.
REF_KEYS = {
    "refClassFeature": "classFeature",
    "refSubclassFeature": "subclassFeature",
    "refOptionalfeature": "optionalfeature",
    "refFeat": "feat",
}

# {@filter display text|page|key=value|key=value}
_FILTER_RE = re.compile(r"\{@filter ([^|}]+)\|([^|}]+)((?:\|[^}]*)?)\}")

# The 2024 rules reprint the 2014 options. When a feature asks for a whole category
# without naming a source, keep the other edition's version of those options out.
# Anything outside these sets (custom uploads) is never filtered out.
_SOURCES_2024 = frozenset({"XPHB", "XDMG", "XMM", "FRHoF"})


def _edition_of(source: Optional[str]) -> Optional[str]:
    """'2024', '2014', or None for sources whose edition we don't know."""
    if not source:
        return None
    code = str(source).upper()
    if code in {s.upper() for s in _SOURCES_2024}:
        return "2024"
    if code in {s.upper() for s in SOURCE_FULL}:
        return "2014"
    return None


def _uid_parts(ref: str) -> Tuple[str, Optional[str]]:
    """Split a 'Name|SOURCE' reference into its name and source."""
    parts = ref.split("|")
    name = parts[0].strip()
    source = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    return name, source


def _contains_ref(entry: Any) -> bool:
    """True if this entry has a feature reference nested anywhere inside it."""
    if isinstance(entry, dict):
        if entry.get("type") in REF_KEYS:
            return True
        return any(_contains_ref(v) for v in entry.values())
    if isinstance(entry, list):
        return any(_contains_ref(e) for e in entry)
    return False


def _iter_strings(entry: Any) -> Iterator[str]:
    if isinstance(entry, str):
        yield entry
    elif isinstance(entry, dict):
        for value in entry.values():
            yield from _iter_strings(value)
    elif isinstance(entry, list):
        for value in entry:
            yield from _iter_strings(value)


class FeatureDetailScreen(Screen):
    """Shared rendering and link navigation for class and optional feature details.

    Feature text refers to other features in two ways, and both become buttons here:
      * explicit `ref*` entries, which may sit at any depth (usually inside an
        `options` wrapper, e.g. the 2014 Fighting Style list)
      * `{@filter ...}` tags naming a whole category of options, e.g. the 2024
        Fighting Style pointing at every feat with category FS
    """

    def __init__(self) -> None:
        super().__init__()
        self._refs: Dict[str, Tuple[str, str]] = {}
        self._targets: Dict[str, Any] = {}
        self._seen_filters: set = set()

    # ── theming helpers ──────────────────────────────────────────────────────

    def _label_color(self) -> str:
        return THEME_LABEL_COLORS.get(self.app.theme, _DEFAULT_LABEL_COLOR)

    def _stat(self, label: str, value: str) -> Static:
        t = Text()
        t.append(label, style=f"bold {self._label_color()}")
        t.append(f" {value}")
        return Static(t)

    # ── entry composition ────────────────────────────────────────────────────

    def _compose_entries(self, entries: List[Any]) -> Iterator[Any]:
        """Yield widgets for entries, turning feature references into buttons."""
        self._refs.clear()
        self._targets.clear()
        self._seen_filters.clear()
        buffer: List[str] = []

        def flush_buffer() -> Iterator[Any]:
            if buffer:
                yield Static("\n\n".join(buffer))
                yield Static("")
                buffer.clear()

        for kind, payload in self._iter_chunks(entries):
            if kind == "text":
                if payload:
                    buffer.append(payload)
            elif kind == "ref":
                yield from flush_buffer()
                yield self._ref_button(payload)
            elif kind == "options":
                yield from flush_buffer()
                yield from self._option_widgets(payload)
        yield from flush_buffer()

    def _iter_chunks(self, entries: List[Any]) -> Iterator[Tuple[str, Any]]:
        """Flatten entries into ('text', markup), ('ref', ref) and ('options', link) chunks."""
        lc = self._label_color()

        for entry in entries:
            ref_info = self._extract_ref(entry)
            if ref_info is not None:
                yield ("ref", ref_info)
                continue

            # A wrapper around references (options / entries / list): keep any heading
            # it carries, then descend so the nested references become buttons too.
            if isinstance(entry, dict) and _contains_ref(entry):
                name = entry.get("name")
                if name:
                    yield ("text", f"[bold {lc}]{self._strip_tags(str(name))}[/bold {lc}]")
                children = entry.get("entries")
                if children is None:
                    children = entry.get("items", [])
                if not isinstance(children, list):
                    children = [children]
                yield from self._iter_chunks(children)
                continue

            yield ("text", self._format_entries([entry]))
            for link in self._filter_links(entry):
                yield ("options", link)

    @staticmethod
    def _extract_ref(entry: Any) -> Optional[Tuple[str, str]]:
        if not isinstance(entry, dict):
            return None
        ref_type = entry.get("type")
        key = REF_KEYS.get(ref_type)
        if key is None:
            return None
        return (ref_type, entry.get(key) or "")

    def _ref_button(self, ref_info: Tuple[str, str]) -> Button:
        ref_type, ref_str = ref_info
        name = ref_str.split("|")[0] if ref_str else "(unknown)"
        button_id = f"ref_{len(self._refs)}"
        self._refs[button_id] = (ref_type, ref_str)
        return Button(f"→ {name}", id=button_id, classes="ref-link")

    # ── {@filter} category links ─────────────────────────────────────────────

    def _filter_links(self, entry: Any) -> List[Tuple[str, str, Dict[str, List[str]]]]:
        """Collect (display text, page, filters) for each {@filter} tag in an entry."""
        links = []
        for text in _iter_strings(entry):
            for match in _FILTER_RE.finditer(text):
                display, page, raw_filters = match.group(1), match.group(2), match.group(3)
                filters: Dict[str, List[str]] = {}
                for part in raw_filters.split("|"):
                    if "=" not in part:
                        continue
                    key, _, value = part.partition("=")
                    filters[key.strip().lower()] = [
                        v.strip() for v in value.split(";") if v.strip()
                    ]
                if not filters:
                    continue
                key = (page.strip().lower(), tuple(sorted((k, tuple(v)) for k, v in filters.items())))
                if key in self._seen_filters:
                    continue
                self._seen_filters.add(key)
                links.append((display.strip(), page.strip().lower(), filters))
        return links

    def _option_widgets(self, link: Tuple[str, str, Dict[str, List[str]]]) -> Iterator[Any]:
        display, page, filters = link
        sources = {s.upper() for s in filters.get("source", [])}
        own_edition = _edition_of(getattr(getattr(self, "feature", None), "source", None))
        lc = self._label_color()

        def keep(source: str) -> bool:
            if sources:
                return source.upper() in sources
            other = _edition_of(source)
            return other is None or own_edition is None or other == own_edition

        if page == "optionalfeatures":
            types = {t.upper() for t in filters.get("feature type", [])}
            if not types:
                return
            matches = [
                of
                for of in self.app.data_loader.optionalfeatures
                if types & {t.upper() for t in of.feature_types} and keep(of.source)
            ]
            heading = ", ".join(
                FEATURE_TYPE_LABELS.get(t, t) for t in sorted(types)
            ) + " options"
        elif page == "feats":
            categories = {c.upper() for c in filters.get("category", [])}
            if not categories:
                return
            matches = [
                ft
                for ft in self.app.data_loader.feats
                if (ft.category or "").upper() in categories and keep(ft.source)
            ]
            heading = f"{display} options"
        else:
            return

        yield Static(f"[bold {lc}]{heading}[/bold {lc}]")
        if not matches:
            yield Static("[dim]None available — the source may not be installed.[/dim]")
            yield Static("")
            return

        for target in sorted(matches, key=lambda t: (t.name, t.source)):
            button_id = f"target_{len(self._targets)}"
            self._targets[button_id] = target
            src = SOURCE_SHORT.get(target.source, target.source)
            yield Button(f"→ {target.name} ({src})", id=button_id, classes="ref-link")
        yield Static("")

    # ── reference resolution ─────────────────────────────────────────────────

    def _resolve_ref(self, ref_type: str, ref_str: str) -> Optional[Any]:
        if not ref_str:
            return None
        parts = ref_str.split("|")

        if ref_type == "refOptionalfeature":
            name, source = _uid_parts(ref_str)
            return self._find_named(self.app.data_loader.optionalfeatures, name, source or "PHB")

        if ref_type == "refFeat":
            name, source = _uid_parts(ref_str)
            return self._find_named(self.app.data_loader.feats, name, source or "PHB")

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

    @staticmethod
    def _find_named(collection: List[Any], name: str, source: str) -> Optional[Any]:
        """Look up by name and source, tolerating the casing 5etools uses in references."""
        name_l = name.lower()
        source_l = source.lower()
        fallback = None
        for entry in collection:
            if entry.name.lower() != name_l:
                continue
            if entry.source.lower() == source_l:
                return entry
            if fallback is None:
                fallback = entry
        return fallback

    def _open_target(self, target: Any) -> None:
        """Push the detail screen matching the target's type."""
        from ..models import ClassFeature, Feat, OptionalFeature

        if isinstance(target, ClassFeature):
            from .class_feature_detail import ClassFeatureDetailScreen

            self.app.push_screen(ClassFeatureDetailScreen(target))
        elif isinstance(target, OptionalFeature):
            from .optional_feature_detail import OptionalFeatureDetailScreen

            self.app.push_screen(OptionalFeatureDetailScreen(target))
        elif isinstance(target, Feat):
            from .feat_detail import FeatDetailScreen

            self.app.push_screen(FeatDetailScreen(target))

    # ── text rendering ───────────────────────────────────────────────────────

    def _strip_tags(self, text: str) -> str:
        text = re.sub(r"\{@filter ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@action ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@condition ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@item ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@spell ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@creature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@feat ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@optfeature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
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
                if e_type in REF_KEYS:
                    ref = entry.get(REF_KEYS[e_type], "")
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

    # ── navigation ───────────────────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            unwind_feature_screens(self.app)
            self.app.action_focus_search()
            event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.app.pop_screen()
            return

        if button_id in self._targets:
            self._open_target(self._targets[button_id])
            return

        if button_id in self._refs:
            ref_type, ref_str = self._refs[button_id]
            target = self._resolve_ref(ref_type, ref_str)
            if target is not None:
                self._open_target(target)
            else:
                name = ref_str.split("|")[0] if ref_str else "feature"
                self.app.notify(
                    f"Could not find '{name}' — the source may not be installed.",
                    severity="warning",
                )


def unwind_feature_screens(app: Any) -> None:
    """Close the whole chain of feature detail screens, back to the list view."""
    if len(app.screen_stack) > 1:
        app.pop_screen()
    while len(app.screen_stack) > 1 and isinstance(app.screen_stack[-1], FeatureDetailScreen):
        app.pop_screen()
