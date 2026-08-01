import re
from typing import Any, Dict, Generator, List, Optional, Tuple

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, TabbedContent, TabPane, Tabs

from ..models import Monster
from ..services import SOURCE_FULL
from ..themes import THEME_LABEL_COLORS, THEME_SECTION_COLORS, _DEFAULT_LABEL_COLOR, _DEFAULT_SECTION_COLOR
from ._entry_format import format_quote, format_table, strip_reference_tags

_ATK_MAP = {
    "m":     "Melee Attack",
    "mw":    "Melee Weapon Attack",
    "rw":    "Ranged Weapon Attack",
    "ms":    "Melee Spell Attack",
    "rs":    "Ranged Spell Attack",
    "mp":    "Melee Power Attack",
    "rp":    "Ranged Power Attack",
    "mw,rw": "Melee or Ranged Weapon Attack",
    "ms,rs": "Melee or Ranged Spell Attack",
    "mp,rp": "Melee or Ranged Power Attack",
}

_ATKR_MAP = {
    "m":   "Melee Attack Roll",
    "r":   "Ranged Attack Roll",
    "m,r": "Melee or Ranged Attack Roll",
}

_SECTIONS: List[Tuple[str, str]] = [
    ("trait",     "Traits"),
    ("action",    "Actions"),
    ("bonus",     "Bonus Actions"),
    ("reaction",  "Reactions"),
    ("legendary", "Legendary Actions"),
]

# Spellcasting frequency groups: JSON key → suffix appended to the use count.
_SPELL_FREQ: List[Tuple[str, str]] = [
    ("rest",      "/rest"),
    ("restShort", "/short rest"),
    ("restLong",  "/long rest"),
    ("daily",     "/day"),
    ("weekly",    "/week"),
    ("monthly",   "/month"),
    ("yearly",    "/year"),
    ("legendary", " legendary action"),
]


_ALIGNMENT_ABV = {
    "L": "Lawful", "N": "Neutral", "C": "Chaotic",
    "G": "Good", "E": "Evil", "U": "Unaligned", "A": "Any",
    # Axis-neutral markers, only meaningful inside the groupings below.
    "NX": "Neutral", "NY": "Neutral",
}
_ETHICAL_AXIS = frozenset({"L", "NX", "C"})
_MORAL_AXIS = frozenset({"G", "NY", "E"})


def _alignment_grouping(codes: List[str]) -> Optional[str]:
    """Collapse a full axis of alignments into 5etools' shorthand, e.g. 'any evil alignment'."""
    present = set(codes)
    if len(present) == 5:
        for missing, text in [
            ("G", "any non-good alignment"),
            ("E", "any non-evil alignment"),
            ("L", "any non-lawful alignment"),
            ("C", "any non-chaotic alignment"),
        ]:
            if missing not in present:
                return text
    if len(present) == 4:
        if _ETHICAL_AXIS <= present:
            if "G" in present:
                return "any good alignment"
            if "E" in present:
                return "any evil alignment"
        if _MORAL_AXIS <= present:
            if "L" in present:
                return "any lawful alignment"
            if "C" in present:
                return "any chaotic alignment"
    if present == {"N", "NX", "NY"}:
        return "any neutral alignment"
    return None


def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


class MonsterDetailScreen(Screen):
    """Detail screen for a single monster stat block."""

    def __init__(self, monster: Monster) -> None:
        super().__init__()
        self.monster = monster

    def _label_color(self) -> str:
        return THEME_LABEL_COLORS.get(self.app.theme, _DEFAULT_LABEL_COLOR)

    def _section_color(self) -> str:
        return THEME_SECTION_COLORS.get(self.app.theme, _DEFAULT_SECTION_COLOR)

    def _stat(self, label: str, value: str) -> Static:
        t = Text()
        t.append(label, style=f"bold {self._label_color()}")
        t.append(f" {value}")
        return Static(t)

    def compose(self) -> ComposeResult:
        m = self.monster
        with Vertical():
            yield Static(f"[bold]{m.name}[/bold]", classes="title")
            with TabbedContent(initial="stat-block"):
                with TabPane("Stat Block", id="stat-block"):
                    with ScrollableContainer():
                        yield Static(
                            f"{m.size_display} {m.type_display}, {self._format_alignment(m.alignment)}"
                        )
                        yield Static("")
                        yield self._stat("Armor Class", self._format_ac(m.ac))
                        yield self._stat("Hit Points", self._format_hp(m.hp))
                        yield self._stat("Speed", self._format_speed(m.speed))
                        yield Static("")
                        yield Static(self._format_ability_scores(m))
                        yield Static("")

                        if m.save:
                            yield self._stat("Saving Throws", self._format_kv(m.save))
                        if m.skill:
                            yield self._stat("Skills", self._format_kv(m.skill))
                        if m.vulnerable:
                            yield self._stat("Damage Vulnerabilities", self._format_resist_immune(m.vulnerable))
                        if m.resist:
                            yield self._stat("Damage Resistances", self._format_resist_immune(m.resist))
                        if m.immune:
                            yield self._stat("Damage Immunities", self._format_resist_immune(m.immune))
                        if m.conditionImmune:
                            yield self._stat("Condition Immunities", self._format_resist_immune(m.conditionImmune))
                        if m.senses:
                            yield self._stat("Senses", ", ".join(m.senses))
                        if m.languages:
                            yield self._stat("Languages", ", ".join(m.languages))
                        yield self._stat("Challenge", m.cr_display)
                        yield Static("")

                        sc = self._section_color()
                        for section_label, items in self._build_sections(m):
                            yield Static(f"[bold {sc}]{section_label}[/bold {sc}]")
                            for text in items:
                                yield Static(text)
                                yield Static("")

                        grp = m.legendary_group_data or {}
                        for grp_key, grp_label in [
                            ("lairActions",    "Lair Actions"),
                            ("regionalEffects", "Regional Effects"),
                        ]:
                            entries = grp.get(grp_key)
                            if entries:
                                yield Static(f"[bold {sc}]{grp_label}[/bold {sc}]")
                                yield Static(self._format_entries(entries))
                                yield Static("")

                        yield Static(f"[dim]Source: {SOURCE_FULL.get(m.source, m.source)}[/dim]")

                with TabPane("Info", id="info"):
                    with ScrollableContainer():
                        if m.fluff:
                            yield Static(self._format_entries(
                                m.fluff,
                                header_color=self._section_color(),
                                label_color=self._label_color(),
                            ))
                        else:
                            yield Static("[dim]No description available for this monster.[/dim]")

            yield Button("Back", id="back")

    def on_mount(self) -> None:
        self.query_one(Tabs).focus()

    def on_key(self, event: events.Key) -> None:
        focused = self.app.focused

        if event.key in ("up", "down") and isinstance(focused, Tabs):
            active_id = self.query_one(TabbedContent).active
            try:
                scroller = self.query_one(f"#stat-block ScrollableContainer" if active_id == "stat-block" else f"#info ScrollableContainer", ScrollableContainer)
                if event.key == "up":
                    scroller.scroll_up()
                else:
                    scroller.scroll_down()
            except Exception:
                pass
            event.stop()

        elif event.key == "tab" and isinstance(focused, Tabs):
            self.query_one("#back", Button).focus()
            event.stop()

        elif event.key == "escape":
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()

    def _build_sections(
        self, m: Monster
    ) -> Generator[Tuple[str, List[str]], None, None]:
        buckets: Dict[str, List[str]] = {key: [] for key, _ in _SECTIONS}

        for sc in m.spellcasting or []:
            # 5etools treats spellcasting as a trait unless displayAs says otherwise;
            # older books (MM 2014 etc.) omit the key entirely.
            display_as = sc.get("displayAs", "trait")
            if display_as in buckets:
                buckets[display_as].append(self._format_spellcasting(sc))

        for feat in m.trait or []:
            buckets["trait"].append(self._format_feature(feat))
        for feat in m.action or []:
            buckets["action"].append(self._format_feature(feat))
        for feat in m.bonus or []:
            buckets["bonus"].append(self._format_feature(feat))
        for feat in m.reaction or []:
            buckets["reaction"].append(self._format_feature(feat))
        for feat in m.legendary or []:
            buckets["legendary"].append(self._format_feature(feat))

        for key, label in _SECTIONS:
            if buckets[key]:
                yield label, buckets[key]

    def _strip_tags(self, text: str) -> str:
        # Resolve innermost tags first, then loop — some sources nest tags,
        # e.g. Flee, Mortals! writes {@sup {@cite Casting Times|FleeMortals|A}}.
        for _ in range(4):
            before = text
            text = re.sub(r"\{@actTrigger\}", "Trigger:", text)
            text = re.sub(r"\{@actResponse(?:\s+\w+)?\}", "Response:", text)
            text = re.sub(r"\{@actSave\s+\w+\}", "", text)
            text = re.sub(r"\{@actSaveFail\}", "On a failed save:", text)
            text = re.sub(r"\{@actSaveSuccess\}", "On a successful save:", text)
            text = re.sub(r"\{@actSaveSuccessOrFail\}", "On a failed or successful save:", text)
            text = re.sub(r"\{@hom\}", "Hit or Miss: ", text)
            text = re.sub(r"\{@hitYourSpellAttack\}", "your spell attack modifier", text)
            text = re.sub(r"\{@dcYourSpellSave\}", "your spell save DC", text)
            text = re.sub(
                r"\{@recharge\s*(\d+)?\}",
                lambda m: f"(Recharge {m.group(1)}-6)" if m.group(1) else "(Recharge 6)",
                text,
            )
            text = re.sub(
                r"\{@atk ([^{}]+)\}",
                lambda m: _ATK_MAP.get(m.group(1).strip(), m.group(1)),
                text,
            )
            text = re.sub(
                r"\{@atkr ([^{}]+)\}",
                lambda m: _ATKR_MAP.get(m.group(1).strip(), m.group(1)),
                text,
            )
            text = re.sub(r"\{@h\}", "", text)
            text = re.sub(r"\{@hit ([^{}]+)\}", r"+\1", text)
            text = re.sub(r"\{@dc ([^{}]+)\}", r"DC \1", text)
            text = re.sub(r"\{@(?:damage|dice) ([^{}]+)\}", r"\1", text)
            # Superscript footnote markers carry no meaning in a terminal.
            text = re.sub(r"\{@sup [^{}]*\}", "", text)
            text = strip_reference_tags(text)
            if text == before:
                break
        # Clean up artifacts left by stripped tags (bare commas, extra spaces)
        text = re.sub(r",\s*,", ",", text)
        text = re.sub(r"^\s*,\s*|\s*,\s*$", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def _format_alignment(self, alignment: List[Any]) -> str:
        def expand(codes: List[Any]) -> str:
            codes = [c for c in codes if isinstance(c, str)]
            return _alignment_grouping(codes) or " ".join(
                _ALIGNMENT_ABV.get(c, c) for c in codes
            )

        if not alignment:
            return "—"

        # Some creatures list weighted alternatives instead of plain codes, e.g. Cloud Giant is
        # [{"alignment": ["N","G"], "chance": 50}, {"alignment": ["N","E"], "chance": 50}]
        if any(isinstance(e, dict) for e in alignment):
            parts = []
            for entry in alignment:
                codes = entry.get("alignment", []) if isinstance(entry, dict) else [entry]
                text = expand(codes)
                if not text:
                    continue
                chance = entry.get("chance") if isinstance(entry, dict) else None
                parts.append(f"{text} ({chance}%)" if chance else text)
            return " or ".join(parts) if parts else "—"

        return expand(alignment) or "—"

    def _format_ac(self, ac: List[Any]) -> str:
        parts: List[str] = []
        for entry in ac:
            if isinstance(entry, int):
                parts.append(str(entry))
                continue
            if not isinstance(entry, dict):
                continue
            # Summoned creatures and similar have no fixed number, only prose.
            if "ac" not in entry and entry.get("special"):
                parts.append(self._strip_tags(str(entry["special"])))
                continue
            value = str(entry.get("ac", "?"))
            armor = entry.get("armor") or entry.get("from", [])
            if armor:
                value += f" ({', '.join(self._strip_tags(str(a)) for a in armor)})"
            condition = entry.get("condition")
            if condition:
                value += f" {self._strip_tags(str(condition))}"
            if entry.get("braces"):
                value = f"({value})"
            parts.append(value)

        if not parts:
            return "—"
        # A braced entry qualifies the one before it: "12 (15 with mage armor)".
        result = parts[0]
        for part in parts[1:]:
            result += f" {part}" if part.startswith("(") else f", {part}"
        return result

    def _format_hp(self, hp: Dict[str, Any]) -> str:
        if "special" in hp:
            return str(hp["special"])
        avg = hp.get("average", "?")
        formula = hp.get("formula")
        return f"{avg} ({formula})" if formula else str(avg)

    def _format_speed(self, speed: Dict[str, Any]) -> str:
        parts = []
        for mode, label in [
            ("walk", ""), ("fly", "fly"), ("swim", "swim"),
            ("burrow", "burrow"), ("climb", "climb"),
        ]:
            val = speed.get(mode)
            if val is None:
                continue
            dist = val if isinstance(val, int) else val.get("number", val)
            text = f"{dist} ft."
            if label:
                text = f"{label} {text}"
            parts.append(text)
        return ", ".join(parts) if parts else "—"

    def _format_ability_scores(self, m: Monster) -> str:
        def mod(score: int) -> str:
            v = (score - 10) // 2
            return f"+{v}" if v >= 0 else str(v)

        scores = [
            ("STR", m.str), ("DEX", m.dex), ("CON", m.con),
            ("INT", m.int), ("WIS", m.wis), ("CHA", m.cha),
        ]
        return "  ".join(
            f"[bold]{name}[/bold] {val} ({mod(val)})" for name, val in scores
        )

    def _format_kv(self, d: Dict[str, str]) -> str:
        return ", ".join(f"{k.upper()} {v}" for k, v in d.items())

    def _format_resist_immune(self, items: List[Any]) -> str:
        parts = []
        for item in items:
            if isinstance(item, str):
                parts.append(self._strip_tags(item))
            elif isinstance(item, dict):
                inner = (
                    item.get("immune")
                    or item.get("resist")
                    or item.get("vulnerable")
                    or item.get("conditionImmune")
                    or item.get("special", [])
                )
                if isinstance(inner, list):
                    text = ", ".join(
                        self._strip_tags(x) if isinstance(x, str) else self._format_resist_immune([x])
                        for x in inner
                    )
                else:
                    text = self._strip_tags(str(inner))
                pre_note = item.get("preNote")
                if pre_note:
                    text = f"{self._strip_tags(str(pre_note))} {text}".strip()
                note = item.get("note")
                if note:
                    note = self._strip_tags(str(note))
                    # Some sources already wrap their note in parentheses.
                    text = f"{text} {note}" if note.startswith("(") else f"{text} ({note})"
                text = text.strip()
                if text:
                    parts.append(text)
        return ", ".join(parts) if parts else "—"

    def _format_feature(self, feature: Dict[str, Any]) -> str:
        name = self._strip_tags(feature.get("name", ""))
        body = self._format_entries(feature.get("entries", []))
        return f"[bold]{name}.[/bold] {body}" if name else body

    def _entry_text(self, entries: List[Any]) -> str:
        """Flatten header/footer entries into a single line of text."""
        parts = [
            self._strip_tags(e) if isinstance(e, str) else self._format_entries([e])
            for e in entries or []
        ]
        return " ".join(p for p in parts if p)

    def _spell_list(self, spells: Any) -> str:
        """Render a list of spell entries, skipping ones flagged as hidden."""
        names: List[str] = []
        for spell in spells or []:
            if isinstance(spell, dict):
                if spell.get("hidden"):
                    continue
                spell = spell.get("entry", "")
            text = self._strip_tags(str(spell))
            if text:
                names.append(text)
        return ", ".join(names)

    @staticmethod
    def _sorted_freq(freq: Dict[str, Any]) -> List[Tuple[str, Any]]:
        """Order use counts high to low. Keys may carry an 'e' suffix (e.g. '3e')."""
        def sort_key(item: Tuple[str, Any]) -> Tuple[int, str]:
            count = item[0]
            digits = count[:-1] if count.endswith("e") else count
            try:
                return (-int(digits), count)
            except ValueError:
                return (0, count)

        return sorted(freq.items(), key=sort_key)

    @staticmethod
    def _slot_label(level: int, data: Dict[str, Any]) -> str:
        """Build a leveled-spell label, e.g. 'Cantrips (at will)' or '1st level (4 slots)'."""
        if level == 0:
            return "Cantrips (at will)"
        label = f"{_ordinal(level)} level"
        lower = data.get("lower")
        if lower is not None:
            label = f"{_ordinal(int(lower))}-{label}"
        slots = data.get("slots")
        if slots:
            label += f" ({slots} slot{'s' if slots != 1 else ''})"
        return label

    def _format_spellcasting(self, sc: Dict[str, Any]) -> str:
        name = self._strip_tags(sc.get("name", "Spellcasting"))
        header = self._entry_text(sc.get("headerEntries", []))

        lines: List[str] = []
        lines.append(f"[bold]{name}.[/bold] {header}" if header else f"[bold]{name}[/bold]")

        # Groups listed in "hidden" are already described by the header entries.
        hidden = set(sc.get("hidden") or ())

        for key, label in [("constant", "Constant"), ("will", "At will")]:
            if key in hidden:
                continue
            spell_str = self._spell_list(sc.get(key))
            if spell_str:
                lines.append(f"  {label}: {spell_str}")

        for freq_key, freq_suffix in _SPELL_FREQ:
            if freq_key in hidden:
                continue
            for count, spells in self._sorted_freq(sc.get(freq_key) or {}):
                spell_str = self._spell_list(spells)
                if not spell_str:
                    continue
                each = count.endswith("e")
                uses = f"{count[:-1] if each else count}{freq_suffix}"
                lines.append(f"  {uses}{' each' if each else ''}: {spell_str}")

        if "recharge" not in hidden:
            for roll, spells in self._sorted_freq(sc.get("recharge") or {}):
                spell_str = self._spell_list(spells)
                if spell_str:
                    lines.append(f"  Recharge {roll}-6: {spell_str}")

        if "spells" not in hidden:
            leveled = sc.get("spells") or {}
            for level in sorted(leveled, key=lambda lvl: int(lvl)):
                data = leveled[level] or {}
                spell_str = self._spell_list(data.get("spells"))
                if spell_str:
                    lines.append(f"  {self._slot_label(int(level), data)}: {spell_str}")

        footer = self._entry_text(sc.get("footerEntries", []))
        if footer:
            lines.append(f"  [dim]{footer}[/dim]")

        return "\n".join(lines)

    def _format_entries(
        self,
        entries: List[Any],
        header_color: Optional[str] = None,
        label_color: Optional[str] = None,
    ) -> str:
        """
        Render entry structures as markup.

        The stat block leaves headings plain bold, because its own section
        headers already carry the colour. The Info tab passes the theme's
        section and label colours so its headings and "Habitat:"-style labels
        line up with the stat block's visual hierarchy.
        """
        def heading(text: str) -> str:
            return f"[bold {header_color}]{text}[/bold {header_color}]" if header_color else f"[bold]{text}[/bold]"

        def label(text: str) -> str:
            return f"[bold {label_color}]{text}[/bold {label_color}]" if label_color else f"[bold]{text}[/bold]"

        def render(entry: Any) -> str:
            if isinstance(entry, str):
                return self._strip_tags(entry)
            if isinstance(entry, dict):
                e_type = entry.get("type")
                if e_type == "list":
                    style = entry.get("style", "")
                    items_rendered = []
                    for e in entry.get("items", []):
                        if isinstance(e, dict) and e.get("type") == "item":
                            name = e.get("name", "")
                            if "entry" in e:
                                body = self._strip_tags(e["entry"]) if isinstance(e["entry"], str) else render(e["entry"])
                            elif "entries" in e:
                                body = "\n".join(render(x) for x in e["entries"])
                            else:
                                body = ""
                            if name:
                                items_rendered.append(f"{label(self._strip_tags(name))} {body}".strip())
                            else:
                                items_rendered.append(body)
                        else:
                            if "list-hang" in style:
                                items_rendered.append(render(e))
                            else:
                                items_rendered.append(f"- {render(e)}")
                    body = "\n".join(items_rendered)
                    # A named list titles the group; its items keep their own names
                    list_name = entry.get("name")
                    if list_name:
                        return f"{label(self._strip_tags(str(list_name)))}\n{body}"
                    return body
                if e_type in {"item", "itemSub"}:
                    # itemSub is a sub-entry of the item above it (a beholder's
                    # individual eye rays); 5etools italicises it rather than bolding
                    name = self._strip_tags(str(entry.get("name", "")))
                    if "entries" in entry:
                        body = "\n".join(render(e) for e in entry["entries"])
                    else:
                        raw = entry.get("entry", "")
                        body = self._strip_tags(raw) if isinstance(raw, str) else render(raw)
                    if not name:
                        return body
                    # Names already ending in punctuation don't want another dot
                    sep = "" if name[-1] in ".:!?" else "."
                    if e_type == "itemSub":
                        return f"[italic]{name + sep}[/italic] {body}"
                    return f"{label(name + sep)} {body}"
                if e_type == "quote":
                    return format_quote(entry, render, self._strip_tags)
                if e_type == "table":
                    return format_table(entry, self._strip_tags, self._label_color(), render)
                if e_type in {"entries", "section", "inset", "insetReadaloud"}:
                    header = entry.get("name")
                    body = "\n\n".join(render(e) for e in entry.get("entries", []))
                    if header:
                        return f"{heading(self._strip_tags(header))}\n\n{body}"
                    return body
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
