from textual.containers import Container, Horizontal
from textual.widgets import Input, Label, ListItem, Select

from services import SearchService, SOURCE_SHORT

from models import Feat
from .base import BaseListView
from .feat_detail import FeatDetailScreen


CATEGORY_OPTIONS = [
    ("All Categories", None),
    ("General", "G"),
    ("Origin", "O"),
    ("Fighting Style", "FS"),
    ("Epic Boon", "EB"),
    ("No Category", "none"),
]

SOURCE_OPTIONS = [
    ("All Sources", None),
    ("Player's Handbook (2024)", "XPHB"),
    ("Xanathar's Guide to Everything", "XGE"),
    ("Tasha's Cauldron of Everything", "TCE"),
    ("Bigby Presents: Glory of the Giants", "BGG"),
]


class FeatsView(BaseListView):
    """Feats list with filters."""

    result_noun = "Feats"

    def render_filters(self) -> Container:
        return Horizontal(
            Select(options=CATEGORY_OPTIONS, id="category_filter", allow_blank=False, value=None),
            Select(options=SOURCE_OPTIONS, id="source_filter", allow_blank=False, value=None),
            id="filters",
        )

    def create_list_item(self, feat: Feat) -> ListItem:
        cat = feat.category or "-"
        source = SOURCE_SHORT.get(feat.source, feat.source)
        return ListItem(Label(f"{feat.name} • {cat} • {source}"))

    def on_select_changed(self, event: Select.Changed) -> None:
        self.apply_filters()

    def apply_filters(self) -> None:
        filtered = self.all_items

        source_select = self.query_one("#source_filter", Select)
        if source_select.value is not None:
            filtered = [f for f in filtered if f.source == source_select.value]

        cat_select = self.query_one("#category_filter", Select)
        if cat_select.value is not None:
            val = cat_select.value
            if val == "FS":
                filtered = [f for f in filtered if f.category and f.category.startswith("FS")]
            elif val == "none":
                filtered = [f for f in filtered if not f.category]
            else:
                filtered = [f for f in filtered if f.category == val]

        self.items = filtered
        search_input = self.query_one("#search", Input)
        self.filtered_items = SearchService.search(self.items, search_input.value)
        self.update_results_list()

    def show_detail(self, feat: Feat) -> None:
        self.app.push_screen(FeatDetailScreen(feat))
