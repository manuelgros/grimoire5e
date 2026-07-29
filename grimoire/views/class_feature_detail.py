from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Button, Static

from ..models import ClassFeature
from ..services import SOURCE_FULL, SOURCE_SHORT
from .feature_detail_base import FeatureDetailScreen


class ClassFeatureDetailScreen(FeatureDetailScreen):
    """Detail screen for a single class or subclass feature."""

    def __init__(self, feature: ClassFeature) -> None:
        super().__init__()
        self.feature = feature

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
