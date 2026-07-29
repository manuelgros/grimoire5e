from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import BaseModel

# 5etools featureType codes → display names.
FEATURE_TYPE_LABELS = {
    "AI": "Artificer Infusion",
    "AS": "Arcane Shot",
    "ED": "Elemental Discipline",
    "EI": "Eldritch Invocation",
    "MM": "Metamagic",
    "MV": "Maneuver",
    "MV:B": "Maneuver (Battle Master)",
    "FS:B": "Fighting Style (Bard)",
    "FS:F": "Fighting Style (Fighter)",
    "FS:P": "Fighting Style (Paladin)",
    "FS:R": "Fighting Style (Ranger)",
    "PB": "Pact Boon",
    "RN": "Rune Knight Rune",
    "RP": "Dragonmarked House Renown",
    "OR": "Onomancy Resonant",
    "AF": "Alchemical Formula",
    "EX": "Exploit",
    "OTH": "Other",
}


@dataclass
class OptionalFeature(BaseModel):
    """A 5etools 'optional feature' — Fighting Styles, Invocations, Metamagic, etc."""

    entries: List[Any]
    feature_types: List[str] = field(default_factory=list)
    prerequisite: Optional[List[Dict[str, Any]]] = None
    consumes: Optional[Dict[str, Any]] = None
    is_variant: bool = False

    @property
    def feature_type_display(self) -> str:
        return ", ".join(
            FEATURE_TYPE_LABELS.get(code, code) for code in self.feature_types
        )

    @property
    def has_prerequisite(self) -> bool:
        return bool(self.prerequisite)
