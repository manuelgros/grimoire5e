import re
from typing import Any, List

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from ..models import Item
from ..services import SOURCE_FULL
from ..themes import THEME_LABEL_COLORS, _DEFAULT_LABEL_COLOR

_RARITY_COLORS = {
    "Uncommon":  "#55cc55",
    "Rare":      "#55cccc",
    "Very Rare": "#cc55cc",
    "Legendary": "#ffd700",
    "Artifact":  "#cc5555",
}


class ItemDetailScreen(Screen):
    """Detail screen for a single magic item."""

    def __init__(self, item: Item) -> None:
        super().__init__()
        self.item = item

    def _label_color(self) -> str:
        return THEME_LABEL_COLORS.get(self.app.theme, _DEFAULT_LABEL_COLOR)

    def _stat(self, label: str, value: str) -> Static:
        t = Text()
        t.append(label, style=f"bold {self._label_color()}")
        t.append(f" {value}")
        return Static(t)

    def _rarity_stat(self, rarity: str) -> Static:
        t = Text()
        t.append("Rarity:", style=f"bold {self._label_color()}")
        t.append(" ")
        color = _RARITY_COLORS.get(rarity)
        t.append(rarity, style=color if color else "")
        return Static(t)

    def compose(self) -> ComposeResult:
        it = self.item
        with Vertical():
            yield Static(f"[bold]{it.name}[/bold]", classes="title")
            yield Static(f"[bold]{it.type_display}[/bold]")
            if it.requires_str:
                yield self._stat("Applies to:", it.requires_str)
            yield self._rarity_stat(it.rarity_display)
            if it.requires_attunement:
                t = Text(it.attunement_display, style="italic")
                yield Static(t)
            if it.poisonTypes:
                delivery = ", ".join(t.title() for t in it.poisonTypes)
                yield self._stat("Delivery:", delivery)
            if it.weight is not None:
                yield self._stat("Weight:", f"{it.weight} lb.")
            if it.value is not None:
                yield self._stat("Value:", self._format_value(it.value))
            yield Static("")

            with ScrollableContainer():
                if it.entries:
                    yield Static(self._format_entries(it.entries))
                else:
                    mechanical = self._format_mechanical_stats(it)
                    if mechanical:
                        yield Static(mechanical)
                yield Static(f"\n[dim]Source: {SOURCE_FULL.get(it.source, it.source)}[/dim]")

            yield Button("Back", id="back")

    _DMG_TYPE_MAP = {
        "S": "slashing", "P": "piercing", "B": "bludgeoning",
        "F": "fire", "C": "cold", "L": "lightning", "A": "acid",
        "N": "necrotic", "R": "radiant", "T": "thunder", "O": "force",
        "Y": "psychic", "I": "poison",
    }

    _PROPERTY_MAP = {
        "2H": "Two-Handed", "A": "Ammunition", "AF": "Ammunition (Firearm)",
        "BF": "Burst Fire", "F": "Finesse", "H": "Heavy", "L": "Light",
        "LD": "Loading", "R": "Reach", "RLD": "Reload", "S": "Special",
        "T": "Thrown", "V": "Versatile",
    }

    def _format_mechanical_stats(self, it) -> str:
        lines = []
        lc = self._label_color()

        # Weapon damage
        if it.dmg1:
            dmg_type = self._DMG_TYPE_MAP.get(it.dmgType or "", it.dmgType or "")
            dmg_str = f"{it.dmg1} {dmg_type}".strip()
            if it.dmg2:
                dmg_str += f" (or {it.dmg2} {dmg_type} two-handed)"
            lines.append(f"[bold {lc}]Damage:[/bold {lc}] {dmg_str}")

        # Range
        if it.item_range:
            lines.append(f"[bold {lc}]Range:[/bold {lc}] {it.item_range} ft.")

        # Armor AC
        if it.ac is not None:
            ac_str = str(it.ac)
            # For shields the ac is a bonus; for armor it's the base
            if it.category == "shield":
                ac_str = f"+{it.ac}"
            lines.append(f"[bold {lc}]Armor Class:[/bold {lc}] {ac_str}")

        if it.strength:
            lines.append(f"[bold {lc}]Strength:[/bold {lc}] Requires Str {it.strength}")

        if it.stealth:
            lines.append(f"[bold {lc}]Stealth:[/bold {lc}] Disadvantage")

        # Weapon properties
        if it.weapon_properties:
            prop_names = [self._PROPERTY_MAP.get(p, p) for p in it.weapon_properties]
            lines.append(f"[bold {lc}]Properties:[/bold {lc}] {', '.join(prop_names)}")

        return "\n".join(lines)

    def _format_value(self, value: int) -> str:
        if value >= 100:
            return f"{value // 100} gp"
        if value >= 10:
            return f"{value // 10} sp"
        return f"{value} cp"

    def _strip_tags(self, text: str) -> str:
        def _replace_inherits(m: re.Match) -> str:
            key = m.group(1)
            if "/" in key:
                key = key.split("/")[0]
            return str(self.item.inherits.get(key, m.group(0)))

        text = re.sub(r"\{=([^}]+)\}", _replace_inherits, text)
        text = re.sub(r"\{@action ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@condition ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@item ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@spell ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@creature ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        text = re.sub(r"\{@damage ([^}]+)\}", r"\1", text)
        text = re.sub(r"\{@dice ([^}]+)\}", r"\1", text)
        text = re.sub(r"\{@dc ([^}]+)\}", r"DC \1", text)
        text = re.sub(r"\{@hit ([^}]+)\}", r"+\1", text)
        text = re.sub(r"\{@\w+ ([^|}]+)(?:\|[^}]*)?\}", r"\1", text)
        return text.strip()

    def _format_entries(self, entries: List[Any]) -> str:
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
                    return f"[bold]{name}.[/bold] {body}" if name else body
                if e_type in {"entries", "section"}:
                    header = entry.get("name")
                    body = "\n".join(render(e) for e in entry.get("entries", []))
                    return f"[bold]{header}[/bold]\n{body}" if header else body
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
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
