from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import BaseModel

# Mirrors Parser.FEAT_CATEGORY_TO_FULL in the 5etools source
CATEGORY_LABELS: Dict[str, str] = {
    "D": "Dragonmark",
    "DG": "Dark Gift",
    "G": "General",
    "O": "Origin",
    "FS": "Fighting Style",
    "FS:P": "Fighting Style (Paladin)",
    "FS:R": "Fighting Style (Ranger)",
    "EB": "Epic Boon",
}


@dataclass
class Feat(BaseModel):
    entries: List[Any]
    prerequisite: Optional[List[Dict[str, Any]]] = None
    ability: Optional[List[Dict[str, Any]]] = None
    repeatable: Optional[bool] = False
    category: Optional[str] = None

    @property
    def has_prerequisite(self) -> bool:
        return self.prerequisite is not None and len(self.prerequisite) > 0

    @property
    def category_display(self) -> str:
        """Full category name for list views; "-" when the feat has none."""
        if not self.category:
            return "-"
        return CATEGORY_LABELS.get(self.category, self.category)
