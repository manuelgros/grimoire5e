from typing import Any, List, Set

from textual.containers import Container, Horizontal
from textual.widgets import Input, Label, ListItem, Select

from ..services import SearchService, SOURCE_FULL, SOURCE_SHORT
from ..models import ClassFeature
from .base import BaseListView
from .class_feature_detail import ClassFeatureDetailScreen


def _build_source_opts(items: List[ClassFeature], active_sources: Set[str]) -> list:
    from ..config import get_custom_sources
    present = {cf.source for cf in items}
    all_sources = {**SOURCE_FULL, **get_custom_sources()}
    return [("All Sources", None)] + [
        (title, code)
        for code, title in all_sources.items()
        if code in active_sources and code in present
    ]


def _build_class_opts(items: List[ClassFeature]) -> list:
    names = sorted({cf.class_name for cf in items})
    return [("All Classes", None)] + [(n, n) for n in names]


def _build_subclass_opts(items: List[ClassFeature], class_name: str | None) -> list:
    if class_name is None:
        return [("All Subclasses", None)]
    subs = sorted({
        cf.subclass_display
        for cf in items
        if cf.class_name == class_name and cf.is_subclass and cf.subclass_display
    })
    return [("All Subclasses", None), ("Base class only", "__base__")] + [(s, s) for s in subs]


_LEVEL_OPTS = [("All Levels", None)] + [(f"Level {i}", i) for i in range(1, 21)]


class ClassFeaturesView(BaseListView):
    """Class & subclass features list with filters."""

    result_noun = "Features"

    def __init__(self, items: List[Any], active_sources: Set[str] = frozenset(), **kwargs: Any) -> None:
        super().__init__(items, **kwargs)
        self._active_sources = set(active_sources)

    def render_filters(self) -> Container:
        return Horizontal(
            Select(options=_build_class_opts(self.all_items), id="class_filter", allow_blank=False, value=None),
            Select(options=_build_subclass_opts(self.all_items, None), id="subclass_filter", allow_blank=False, value=None),
            Select(options=_LEVEL_OPTS, id="level_filter", allow_blank=False, value=None),
            Select(
                options=_build_source_opts(self.all_items, self._active_sources),
                id="source_filter",
                allow_blank=False,
                value=None,
            ),
            id="filters",
        )

    def create_list_item(self, cf: ClassFeature) -> ListItem:
        src = SOURCE_SHORT.get(cf.source, cf.source)
        if cf.is_subclass and cf.subclass_display:
            who = f"{cf.class_name} ({cf.subclass_display})"
        else:
            who = cf.class_name
        variant = " [dim][variant][/dim]" if cf.is_variant else ""
        return ListItem(Label(f"{cf.name} • {who} L{cf.level} • {src}{variant}"))

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "class_filter":
            sub_select = self.query_one("#subclass_filter", Select)
            sub_select.set_options(_build_subclass_opts(self.all_items, event.value))
            sub_select.value = None
        self.apply_filters()

    def apply_filters(self) -> None:
        filtered = self.all_items

        source_select = self.query_one("#source_filter", Select)
        if source_select.value is not None:
            filtered = [cf for cf in filtered if cf.source == source_select.value]

        class_select = self.query_one("#class_filter", Select)
        if class_select.value is not None:
            filtered = [cf for cf in filtered if cf.class_name == class_select.value]

        sub_select = self.query_one("#subclass_filter", Select)
        if sub_select.value == "__base__":
            filtered = [cf for cf in filtered if not cf.is_subclass]
        elif sub_select.value is not None:
            filtered = [cf for cf in filtered if cf.subclass_display == sub_select.value]

        level_select = self.query_one("#level_filter", Select)
        if level_select.value is not None:
            filtered = [cf for cf in filtered if cf.level == level_select.value]

        self.items = filtered
        search_input = self.query_one("#search", Input)
        self.filtered_items = SearchService.search(self.items, search_input.value)
        self.update_results_list()

    def reload(self, new_items: List[Any], active_sources: Set[str]) -> None:
        self._active_sources = set(active_sources)
        self.all_items = new_items
        self.items = new_items
        self.filtered_items = new_items

        source_select = self.query_one("#source_filter", Select)
        source_select.set_options(_build_source_opts(new_items, active_sources))
        if source_select.value not in active_sources:
            source_select.value = None

        class_select = self.query_one("#class_filter", Select)
        class_select.set_options(_build_class_opts(new_items))
        if class_select.value is not None and class_select.value not in {cf.class_name for cf in new_items}:
            class_select.value = None

        sub_select = self.query_one("#subclass_filter", Select)
        sub_select.set_options(_build_subclass_opts(new_items, class_select.value))
        sub_select.value = None

        if self._loaded:
            self.apply_filters()

    def show_detail(self, cf: ClassFeature) -> None:
        self.app.push_screen(ClassFeatureDetailScreen(cf))
