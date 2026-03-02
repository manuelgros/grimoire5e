from textual.widgets import Label, ListItem

from services import SOURCE_SHORT

from models import Condition
from .base import BaseListView
from .condition_detail import ConditionDetailScreen


class ConditionsView(BaseListView):
    """Conditions list with search."""

    result_noun = "Conditions"

    def create_list_item(self, condition: Condition) -> ListItem:
        source = SOURCE_SHORT.get(condition.source, condition.source)
        return ListItem(Label(f"{condition.name} • {source}"))

    def show_detail(self, condition: Condition) -> None:
        self.app.push_screen(ConditionDetailScreen(condition))
